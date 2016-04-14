class MatchModeEnum(object):
    Contains = 0
    WholeWord = 1
    StartsWidth = 2
    EndsWith = 3
    RegularExpression = 4


class InsertBlockDirectionEnum(object):
    AfterInsert = 0
    BeforeInsert = 1


class MoveBlockDirectionEnum(object):
    AfterMove = 0
    BeforeMove = 1


class InsertDirectionEnum(object):
    LeftInsert = 0
    RightInsert = 1
    TopInsert = 2
    BottomInsert = 3


class MoveDirectionEnum(object):
    LeftMove = 0
    RightMove = 1
    TopMove = 2
    BottomMove = 3
