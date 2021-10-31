from typing import List, Optional
from fastapi import Request

class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")

    async def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append("Kullanıcı Adı Uzunluğu 3'ten Büyük Olmalı")
        if self.username.__contains__(" "):
            self.errors.append("Kullanıcı Adı Boşluk İçermemeli")
        if not self.errors:
            return True
        return False