class Test_for_function:
    """Тестирует, есть ли сообщения с датой, указанной пользователем"""

    def __init__(self):
        pass

    def test_data_list(self, data_list):
        if data_list:
            return True
        else:
            return False
