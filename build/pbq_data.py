"""CySA+ performance-based exercises — hands-on, scored, mapped to CS0-003.

Original scenarios and explanations written against CompTIA's published
objectives. The class PBQ simulations in S:\\CySA+\\PBQSIM were read for the
*skills they exercise* only; no scenario text, answer option or explanation
from them is reproduced here, because this repo is public.

Shape of a PBQ:
    id          stable key, used in localStorage
    obj         CS0-003 objective it scores against
    title       short name
    scenario    the situation, as an analyst would receive it
    task        what the learner has to do
    order       the correct sequence (list of stage names)
    evidence    [{text, stage, why}] — one artifact per stage, shuffled on load

Both halves are scored: sequencing the stages, and attributing each artifact
to the right stage.
"""

PBQS = [
{
 'id': 'killchain',
 'obj': '3.1',
 'title': 'Kill Chain Reconstruction',
 'scenario':
   "You are handed a finished timeline from an intrusion at a mid-size engineering "
   "firm. Seven artifacts survived in the logs. The incident lead wants them placed "
   "on the Lockheed Martin Cyber Kill Chain before the report goes out, because the "
   "remediation owner for each stage is different.",
 'task':
   "Put the seven kill chain stages in order, then attribute each artifact to the "
   "stage it belongs to. Two of them are commonly placed one stage too early or too "
   "late — the distinction is what the stage actually describes, not when you first "
   "noticed it.",
 'order': ['Reconnaissance', 'Weaponization', 'Delivery', 'Exploitation',
           'Installation', 'Command and Control', 'Actions on Objectives'],
 'evidence': [
   {'stage': 'Reconnaissance',
    'text': "Three weeks before anything else, a single external address walks the "
            "company's public staff directory and pulls every name and job title.",
    'why':  "Reconnaissance is information gathering about the target, and it leaves "
            "no foothold behind. The giveaway is that nothing is delivered and nothing "
            "runs — the attacker is only learning who exists and what they do, which "
            "is what makes the later email convincing."},
   {'stage': 'Weaponization',
    'text': "A macro-enabled spreadsheet is assembled on the attacker's own "
            "infrastructure, pairing a loader with a finance-themed document.",
    'why':  "Weaponization happens entirely on the attacker's side and never touches "
            "the victim — which is exactly why it is the stage defenders have no "
            "telemetry for. Coupling a payload to a deliverable artifact is the whole "
            "definition. If you placed Delivery here, ask whether the victim has seen "
            "it yet; they have not."},
   {'stage': 'Delivery',
    'text': "That spreadsheet arrives as an attachment addressed to three named "
            "accounts-payable staff, using their correct job titles.",
    'why':  "Delivery is the transmission of the weapon to the target — email, web, "
            "removable media. Note it uses the titles harvested during reconnaissance, "
            "which is how the two stages connect. The email itself is delivery even "
            "though phishing is often loosely described as the whole attack."},
   {'stage': 'Exploitation',
    'text': "One recipient opens the file; the macro executes and spawns a PowerShell "
            "process from the Office application.",
    'why':  "Exploitation is the moment the weapon fires — a vulnerability triggering, "
            "or a user being induced to run something. Office spawning PowerShell is "
            "the classic parent-child anomaly that marks it. Nothing persistent exists "
            "yet; kill the process now and the intrusion ends."},
   {'stage': 'Installation',
    'text': "A scheduled task is registered that relaunches the loader every time the "
            "user signs in.",
    'why':  "Installation is persistence — the attacker arranging to survive a reboot "
            "or a logoff. This is the stage most often confused with Exploitation. The "
            "test is simple: exploitation got code running once, installation makes it "
            "come back."},
   {'stage': 'Command and Control',
    'text': "The host begins reaching an external address every sixty seconds over "
            "HTTPS, each request under a kilobyte.",
    'why':  "Command and control is the channel back to the operator. Small, regular, "
            "low-volume outbound traffic is beaconing — the host asking for "
            "instructions. Until this works the attacker has code on a machine they "
            "cannot steer."},
   {'stage': 'Actions on Objectives',
    'text': "The finance share is archived into a single file, split, and uploaded "
            "over the same channel.",
    'why':  "Actions on objectives is the attacker finally doing the thing they came "
            "for — here, exfiltration. Collection and staging belong to this stage too. "
            "Everything before it was setup; this is the loss."},
 ],
},
]
