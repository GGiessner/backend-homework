import pathlib as pl

import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

data = pl.Path(__file__).parent.absolute() / 'data'

# Charger les données CSV
associations_df = pd.read_csv(data / 'associations_etudiantes.csv')
evenements_df = pd.read_csv(data / 'evenements_associations.csv')

## Vous devez ajouter les routes ici : 

# alive
@app.route( '/api/alive' , methods=['GET'])
def alive():
    return {"message":"Alive"}, 200

# liste association
@app.route( '/api/associations' , methods=['GET'])
def liste_assos():
    return associations_df['id'].tolist(), 200

# détails d'une association

@app.route( '/api/association/<int:id>' , methods=['GET'])
def id_assos(id):
    association=associations_df[associations_df['id']==id]
    if len (association)!=0:
        return association.to_dict(orient='records'),200
    else:
        return { "error": "evenement not found" }, 404
    

# liste évènement
@app.route( '/api/evenements' , methods=['GET'])
def liste_evt():
    return evenements_df['id'].tolist(), 200


# détails d'un évènement

@app.route( '/api/evenement/<int:id>' , methods=['GET'])
def id_evts(id):
    evenement=evenements_df[evenements_df['id']==id]
    if len (evenement)!=0:
        return evenement.to_dict(orient='records'),200
    else:
        return { "error": "evenement not found" }, 404


# liste des évènements d'une association

@app.route( '/api/association/<int:id>/evenements' , methods=['GET'])
def list_evts_asso(id):
    evenement=evenements_df[evenements_df['association_id']==id]
    return evenement['id'].tolist(), 200


# liste des associations par type

@app.route( '/api/associations/type/<type>' , methods=['GET'])
def list_type_asso(type):
    asso=associations_df[associations_df['type']==type]
    return asso['nom'].tolist(), 200






if __name__ == '__main__':
    app.run(debug=False)
