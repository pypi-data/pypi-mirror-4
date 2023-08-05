from random import randint, choice


class KochLesson:
    chars = "kmrsuaptlowi.njef0yv,g5/q9zh38b?427c1d6x"

    def __init__(self, lesson, prefer_last=False, chars_ignored=""):
        self.set_lesson( lesson )
        self.__curr_group_size = randint(1,8)
        self.__char_of_grp     = 0
        self.__chars_send      = 0
        self.__prefer_last     = prefer_last
        self.__chars_ignored   = chars_ignored
 
 
    def __iter__(self):
        return self


    def next(self):
        c = self._get_next_char()
        while c in self.__chars_ignored and c != " ":
            c = self._get_next_char()
        self.__chars_send += 1
        self.__char_of_grp += 1
        return c


    def _get_next_char(self):
        # if group is complete: set next groupsize, 
        # reset counter and return a pause
        if self.__curr_group_size <= self.__char_of_grp:
            self.__curr_group_size = randint(1,8)
            self.__char_of_grp = -1
            return " "
 
        # increment counter and return a random char for current lesson
        if self.__prefer_last:
            def exp_prop(lst):
                if len(lst) <= 1: return lst
                return lst+exp_prop(lst[len(lst)/2:])
            return choice(exp_prop(self.chars[:self.__lesson]))
        else:
            return choice(self.chars[:self.__lesson])


    def get_chars_send(self):
        return self.__chars_send

    def reset_char_counter(self):
        self.__char_of_grp = 0
        self.__chars_send  = 0


    def get_lesson(self):
        return self.__lesson
    
    def set_lesson(self, lesson):
        if not lesson in range(2,41): 
            raise Exception("Ther are only 40 lessons")
        self.__lesson = int(lesson)
    

    def get_preferlast(self):
        return self.__prefer_last

    def set_preferlast(self, prefer):
        self.__prefer_last = prefer

    def set_ignore_chars(self, chars):
        self.__chars_ignored = chars
        
            
