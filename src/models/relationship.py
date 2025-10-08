# src/models/relationship.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import datetime


@dataclass
class RelationshipEvent:
    timestamp: str
    char_id: str
    amount: int
    reason: str
    source: Optional[str] = None


@dataclass
class CharacterRelationship:
    char_id: str
    points: int = 0
    events: List[RelationshipEvent] = field(default_factory=list)


class RelationshipManager:
    """
    RelationshipManager tracks per-character relationship points, computes ranks,
    and provides a festival_interaction hook that may set downgrade-warning flags
    but does NOT apply major punishments automatically in MVP.

    Ranks are defined by `thresholds` (rank -> min points).
    """

    def __init__(self, thresholds: Optional[Dict[int, int]] = None):
        # default thresholds: 0=Neutral,1=Friend,2=Confidant,3=Partner
        if thresholds is None:
            thresholds = {0: 0, 1: 10, 2: 25, 3: 50}
        self.thresholds = dict(sorted(thresholds.items(), key=lambda kv: kv[0]))
        self.relations: Dict[str, CharacterRelationship] = {}
        self.flags: Dict[str, Any] = {}  # general-purpose flags (festival warnings, downgrades, etc.)

        self.rank_names = {
            0: "Neutral",
            1: "Friend",
            2: "Confidant",
            3: "Partner",
        }

    # ---------------- Core API ----------------

    def _now_iso(self) -> str:
        return datetime.datetime.utcnow().isoformat() + "Z"

    def add_points(self, char_id: str, amount: int, reason: str, source: Optional[str] = None) -> int:
        """
        Add relationship points for a character (can be negative).
        Records a RelationshipEvent. Returns the new points total.
        """
        if char_id not in self.relations:
            self.relations[char_id] = CharacterRelationship(char_id=char_id, points=0)
        rel = self.relations[char_id]
        rel.points += amount
        ev = RelationshipEvent(timestamp=self._now_iso(), char_id=char_id, amount=amount, reason=reason, source=source)
        rel.events.append(ev)
        return rel.points

    def get_points(self, char_id: str) -> int:
        return self.relations.get(char_id, CharacterRelationship(char_id=char_id)).points

    def get_rank(self, char_id: str) -> int:
        pts = self.get_points(char_id)
        rank = 0
        for r, thresh in self.thresholds.items():
            if pts >= thresh:
                rank = r
        return rank

    def get_rank_name(self, char_id: str) -> str:
        return self.rank_names.get(self.get_rank(char_id), f"Rank {self.get_rank(char_id)}")

    def list_relationships(self) -> List[Dict[str, Any]]:
        """
        Return list of relationship summaries for UI/tests.
        Each item: {char_id, points, rank, rank_name, last_event (optional)}
        """
        out = []
        for cid, rel in self.relations.items():
            last_event = rel.events[-1].__dict__ if rel.events else None
            out.append({
                "char_id": cid,
                "points": rel.points,
                "rank": self.get_rank(cid),
                "rank_name": self.get_rank_name(cid),
                "last_event": last_event
            })
        return out

    # ---------------- Festival interaction hook ----------------
    def festival_interaction(self, festival_id: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process festival actions.

        actions: list of dicts with keys:
          - actor: player id
          - target: char_id (the NPC)
          - action_type: "give_charm" | "insult" | "cheer" | "skip" | ...
          - amount: optional int (points change)
          - note: optional string for logs

        The hook:
         - applies immediate point changes for benign actions (give_charm, cheer)
         - applies small negative points for insults
         - sets downgrade-warning flags (e.g., "festival_downgrade_warning:{char_id}") when a rule is triggered
           but DOES NOT auto-apply major punishments (like forced rank drop) in MVP.
        Returns summary dict: {"processed": [...], "flags_set": {...}, "points_changes": {...}}
        """
        summary = {"festival_id": festival_id, "processed": [], "flags_set": {}, "points_changes": {}}

        for act in actions:
            actor = act.get("actor")
            target = act.get("target")
            action_type = act.get("action_type")
            amount = act.get("amount")
            note = act.get("note")

            if target is None or action_type is None:
                continue

            # Get rank *before* point modification to check against pre-action state
            rank_before_action = self.get_rank(target)

            # Default behavior mapping
            if amount is None:
                if action_type == "give_charm":
                    amount = 5
                elif action_type == "cheer":
                    amount = 2
                elif action_type == "insult":
                    amount = -6
                elif action_type == "skip":
                    amount = 0
                else:
                    amount = 0

            reason = f"festival:{festival_id}:{action_type}"
            self.add_points(target, amount, reason, source=actor)

            # If negative event (insult) and rank high, set warning flag (do not auto-downgrade)
            if action_type == "insult" and rank_before_action >= 2:
                flag_key = f"festival_downgrade_warning:{festival_id}:{target}"
                self.flags[flag_key] = {
                    "triggered_by": actor,
                    "rank_at_trigger": rank_before_action,
                    "reason": reason,
                    "timestamp": self._now_iso()
                }
                summary["flags_set"][flag_key] = self.flags[flag_key]

            # If a player gives a charm and target is Neutral, small chance to raise priority flag for romance (not auto-apply)
            if action_type == "give_charm" and rank_before_action == 0:
                flag_key = f"festival_romance_interest:{festival_id}:{target}"
                self.flags[flag_key] = {
                    "triggered_by": actor,
                    "reason": reason,
                    "timestamp": self._now_iso()
                }
                summary["flags_set"][flag_key] = self.flags[flag_key]

            summary["processed"].append({
                "actor": actor,
                "target": target,
                "action_type": action_type,
                "applied_amount": amount,
                "reason": reason,
                "resulting_points": self.get_points(target),
                "resulting_rank": self.get_rank(target),
            })
            summary["points_changes"].setdefault(target, 0)
            summary["points_changes"][target] += amount

        return summary

    # ---------------- UI helpers ----------------

    def relationship_panel(self) -> Dict[str, Any]:
        """
        Return a UI-friendly structure summarizing relationships and relevant flags.
        Example:
        {
          "relationships": [ {char_id, points, rank, rank_name} ... ],
          "flags": { ... }
        }
        """
        return {
            "relationships": self.list_relationships(),
            "flags": dict(self.flags)
        }

    def render_relationship_panel(self) -> None:
        """
        Console-friendly rendering (for the console UI).
        """
        panel = self.relationship_panel()
        print("=== Relationship Panel ===")
        for r in panel["relationships"]:
            print(f"{r['char_id']}: {r['points']} pts — {r['rank_name']} (rank {r['rank']})")
            le = r.get("last_event")
            if le:
                print(f"  last: {le['amount']} pts ({le['reason']}) at {le['timestamp']}")
        if panel["flags"]:
            print("\n-- Flags --")
            for k, v in panel["flags"].items():
                print(f"{k} => {v}")
        print("==========================\n")
