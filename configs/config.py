
"""100PrisonerProblem config module"""


NUMBER_OF_PRISONERS = 100
NUMBER_OF_ITERATIONS = 100
METHOD = 1  # 1 - random, 2 - длина цепочек из ролика

LOG_LEVEL = 1
# 0 - только общие сведения,
# 1 - инфа о итерациях,
# 2 - вывод поля при неудаче заключённого
# 3 - выводить инфу по каждому заключённому
# 4 - выводить все ящики у заключённых
# 5 - вывод поля при любом исходе

BREAK_IF_FALSE = False

INDENT_VERTICAL = 0  # 1
INDENT_HORIZONTAL = 1  # 3
COLOR_NUM_BOX = 5
COLOR_OPEN_BOX = 15
COLOR_NUM_PAPER = 3
