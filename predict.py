import pickle
import argparse
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict CSGO player rating based on HLTV 2.0 formula.')
    parser.add_argument('dpr', help='Deaths per round.')
    parser.add_argument('kast', help='Percentage of rounds in which the player either had a kill,assist, survived or was traded.')
    parser.add_argument('impact', help='PMeasures the impact made from multikills, opening kills,and clutched.')
    parser.add_argument('adr', help='Average damage per round.')
    parser.add_argument('kpr', help='Kills per round.')
    args = parser.parse_args()

    X = np.array([[args.dpr, args.kast, args.impact, args.adr, args.kpr]]).astype(np.float32)
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
        y = model.predict(X)
        print(f"Rating: {y}")
