from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import numpy as np
import torch
import torch.nn as nn
import transformers
from transformers import AutoModel, BertTokenizerFast
import uvicorn
from loguru import logger

app = FastAPI()

model_path = "saved_weights.pt"
model = torch.load(model_path, map_location=torch.device("cpu"))
model.eval()


@app.get("/")
def api_status():
    return "api is healthy"


class Message(BaseModel):
    text: str


@app.post("/predict")
async def predict(message: Message):
    try:
        tokenizer = BertTokenizerFast.from_pretrained(
            "bert-base-uncased",
        )
        tokens_test = tokenizer.batch_encode_plus(
            [message.text],
            max_length=25,
            pad_to_max_length=True,
            truncation=True,
            return_token_type_ids=False,
        )
        test_seq = torch.tensor(tokens_test["input_ids"])
        test_mask = torch.tensor(tokens_test["attention_mask"])
        with torch.no_grad():
            preds = model(test_seq.to("cpu"), test_mask.to("cpu"))
            preds = preds.detach().cpu().numpy()
        preds = np.argmax(preds, axis=1)
        return {"prediction": "spam"} if preds == 1 else {"prediction": "ham"}
    except HTTPException as e:
        logger.error(e)
        return {"status": "false", "message": "something went wrong"}


if __name__ == "__main__":
    uvicorn.run(app)
