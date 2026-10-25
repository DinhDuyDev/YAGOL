# @description: SUBJECT YOU WILL BE KILLING

# @section: IMPORTS
import utility

# @section: SUBJECTDEF
class Subject:
    health: utility.numericType = 50
    def heal(healing_rate: utility.numericType):
        Subject.health += healing_rate