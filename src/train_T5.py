from pathlib import Path
from torch.utils.data import DataLoader
import torch
import torch.optim as optim
import transformers
import pandas as pd
import argparse
import json
import os
import tqdm

from transformers import T5Tokenizer, T5ForConditionalGeneration
from datasets import Dataset, DatasetDict
import evaluate


def val(model, tokenizer, val_dataloader, val_dir = None):
  model.eval()
  eval_dict = [] 
  for val_batch in val_dataloader:
    batch = {}
    for k,v in val_batch.items():
      if k in ["input_ids", "labels", "attention_mask"]:
        batch[k] = v.to("cuda")

    with torch.no_grad():
      outputs = model(**batch)
    
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    for i, pred in enumerate(tokenizer.batch_decode(predictions)):
      eval_dict.append({
        "Ques": val_batch['input'][i],
        "Gold": val_batch['label'][i],
        "Gene": pred
      })
    # metric.add_batch(
    #   predictions = predictions,
    #   references = batch["labels"])
  # print(f"Metric: {metric.compute()}")
  # print(f'Accuracy: {metric.compute()}')

  if val_dir:
    with open(val_dir, "w") as f:
      json.dump(eval_dict, f, indent=2)

  model.train()


def main():
    
  parser = argparse.ArgumentParser()

  parser.add_argument("datapath", type=str)
  parser.add_argument("--cuda", type=str, default="0")
  parser.add_argument("--epochs", type=int, default=1)
  parser.add_argument("--saveto", type=str,
                      default=Path(__file__) / "models" / "temp")

  args = parser.parse_args()

  with open(args.datapath) as f:
    data = json.load(f)
  df = pd.DataFrame(data)
  
  os.environ["CUDA_VISIBLE_DEVICES"]= args.cuda

  num_epochs = args.epochs

  saveto = Path(args.saveto)
  saveto.mkdir(parents=True, exist_ok = True)

  # Split dataset
  data_len = len(df)
  train_val_split = 0.9
  train_set = Dataset.from_pandas(df[:round(data_len * train_val_split)])
  val_set = Dataset.from_pandas(df[round(data_len * train_val_split):])

  dataset = DatasetDict()
  dataset['train'] = train_set
  dataset['validation'] = val_set

  # Load Tokenizer
  tokenizer = T5Tokenizer.from_pretrained("t5-small")

  # Tokenize inputs and outputs
  def tokenize_data(dataset, source):
    model_inputs = tokenizer(dataset[source], padding=True,
                             return_tensors="pt")
    return model_inputs

  tokenized_dataset = dataset \
    .map(lambda x: tokenize_data(x, "label"), batched=True) \
    .rename_column("input_ids", "labels") \
    .map(lambda x: tokenize_data(x, "input"), batched=True) \
  
  tokenized_dataset.set_format("torch")

  train_dataset = tokenized_dataset["train"]
  val_dataset = tokenized_dataset["validation"]

  # Load Model
  model = T5ForConditionalGeneration \
    .from_pretrained("t5-small").to("cuda")

  # DataLoader
  train_dataloader = DataLoader(train_dataset, batch_size = 2)
  val_dataloader = DataLoader(val_dataset, batch_size = 2)

  # Train Model
  model.train()

  scalar = 0
  i = 0

  optimizer = optim.AdamW(model.parameters(), lr = 0.0015)
  lr_scheduler=transformers. \
    get_polynomial_decay_schedule_with_warmup(optimizer, 5000, 30000, power=0.5)
  for epoch in range(num_epochs):
    i = 0
    iters = len(train_dataloader)
    for batch in train_dataloader:
      newbatch = {}
      for k,v in batch.items():
        if k not in ["label", "input"]:
          newbatch[k] = v.to("cuda")
      
      batch = newbatch

      outputs = model(**batch)
      loss = outputs.loss
      scalar += loss.mean().item()

      if (i + 1) % 100 == 0:
        print(f'iteration = {i + 1}/{iters}, training loss={scalar/100}')
        scalar = 0

      loss /= 10 
      loss.mean().backward()
      if (i+1) % 10:
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
      
      i += 1
    
    val(model, tokenizer, val_dataloader, saveto / f"val_{epoch}.json")

    torch.save(model.state_dict(),
      saveto / f"cp_{epoch}.pth")

if __name__ == "__main__":
  main()
