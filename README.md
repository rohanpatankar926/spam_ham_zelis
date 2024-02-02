#### workflow


**.github/workflows** --> ci/cd pipeline <br>
**infra** --> for creating a kube cluster IAAC <br>
**app/api_pred.py** --> model inferencing api <br>
**k8s** --> kubernetes manifests <br>
**Dockerfile** --> creating docker image <br>
**preprocess_data.py** --> preprocessing enron raw data <br>
**requirements.txt** --> required python packages <br>
**spam_ham_bert.ipynb** --> finetuning or training the spam-ham dataset and evaluating and saving the model
            
              
              precision    recall  f1-score   support

           0       0.84      0.93      0.88      2858
           1       0.96      0.91      0.93      5651

    accuracy                           0.91      8509
   macro avg       0.90      0.92      0.91      8509
weighted avg       0.92      0.91      0.92      8509
