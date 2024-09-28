# Лекция 1

для работы со средой используй poetry
запуск `uvicorn lecture_1.main:app`

я добавила ещё один тест `("/", HTTPStatus.UNPROCESSABLE_ENTITY)` на отсутствие числа в Фибоначчи, если это неправильно – igrore it.
