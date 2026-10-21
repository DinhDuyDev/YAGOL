# @description: AUDIENCEDEF
# @textdesc: An audience controller 

# @section: IMPORTS
import settings

# @section: SCHEMA
# @textdesc: database schema 
# states database schema
# excitement_bonus: amount of engagement increase
# excitement_deficit: amount of engagement decrease if something takes too long
# time_threshold: time the audience can take for the bossfight to last before they get bored
class AudienceController:
    states = {
        "BOSS_FIGHT": {
            "excitement_bonus": 1000,
            "time_threshold": 40 * settings.SECONDS,
        }
    }