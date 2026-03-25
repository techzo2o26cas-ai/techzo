from pydantic import BaseModel
from ai.predictor import predict_data


class Post(BaseModel):
    post_content: str




class Update(BaseModel):
    post_content: str

    def filter_content(self):
        result = predict_data(self.post_content)

        if result.get("bullying") is True:
            return None
        else:
            return self.post_content
