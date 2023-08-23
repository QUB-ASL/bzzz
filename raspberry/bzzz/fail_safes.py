class FailSafes:
    # Dict keys
    UNKNOWN = -1
    FAILED = 0
    SUCCEEDED = 1

    _fail_safe_ID = "fail_safe_ID"
    _fail_safe_obj = "fail_safe_obj"
    _fail_safe_status = "fail_safe_status"
    _dummy_fail_safe = "dummy_fail_safe"

    def __init__(self):
        # This variable is a dict with the following structure
        # {fail_safe_name: {fail_safe_ID: int, fail_safe_obj: obj, fail_safe_status: FAILED or SUCCEEDED}}
        self.__fail_safe_functions_dict = {}
        self.__last_fail_safe_ID = -1
        self.__added_fail_safes = []

        self.__fail_safe_functions_dict[FailSafes._dummy_fail_safe] = {
            FailSafes._fail_safe_ID: self.__last_fail_safe_ID,
            FailSafes._fail_safe_obj: lambda : print("Dummy fail safe"),
            FailSafes._fail_safe_status: FailSafes.FAILED
            }
        
    def add_fail_safe(self, fail_safe_name, fail_safe_obj):
        self.__last_fail_safe_ID += 1
        self.__added_fail_safes.append(fail_safe_name)
        self.__fail_safe_functions_dict[fail_safe_name] = {
            FailSafes._fail_safe_ID: self.__last_fail_safe_ID,
            FailSafes._fail_safe_obj: fail_safe_obj,
            FailSafes._fail_safe_status: FailSafes.UNKNOWN
            }
        
    def fail_safe_obj(self, fail_safe_name):
        return self.__fail_safe_functions_dict.get(fail_safe_name, self.__fail_safe_functions_dict[FailSafes._dummy_fail_safe]).get(FailSafes._fail_safe_obj)

    def run(self):
        for fail_safe in self.__added_fail_safes:
            status_bool = self.fail_safe_obj(fail_safe)()
            if status_bool:
                self.__fail_safe_functions_dict[fail_safe][FailSafes._fail_safe_status] = FailSafes.SUCCEEDED
            else:
                self.__fail_safe_functions_dict[fail_safe][FailSafes._fail_safe_status] = FailSafes.FAILED
                print(f"Fail safe check of {fail_safe} Failed!!!\n Taking action.....")
                self.fail_safe_obj(fail_safe)(take_action=True)
