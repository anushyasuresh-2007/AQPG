import datasets
import json

def test_v14_candidates():
    print("Testing Phase 14 candidate sources...")
    results = {}
    
    # 1. Test camel-ai/physics
    try:
        print("Testing camel-ai/physics...")
        ds_phy = datasets.load_dataset("camel-ai/physics")
        print(f"camel-ai/physics: {ds_phy}")
        results["camel_physics"] = {"status": "SUCCESS", "splits": {k: len(v) for k, v in ds_phy.items()}}
    except Exception as e:
        print(f"camel-ai/physics failed: {e}")
        results["camel_physics"] = {"status": "FAILED", "error": str(e)}

    # 2. Test camel-ai/chemistry
    try:
        print("Testing camel-ai/chemistry...")
        ds_chem = datasets.load_dataset("camel-ai/chemistry")
        print(f"camel-ai/chemistry: {ds_chem}")
        results["camel_chemistry"] = {"status": "SUCCESS", "splits": {k: len(v) for k, v in ds_chem.items()}}
    except Exception as e:
        print(f"camel-ai/chemistry failed: {e}")
        results["camel_chemistry"] = {"status": "FAILED", "error": str(e)}

    # 3. Test hendrycks_math
    try:
        print("Testing hendrycks/competition_math...")
        ds_math = datasets.load_dataset("hendrycks/competition_math")
        print(f"competition_math: {ds_math}")
        results["competition_math"] = {"status": "SUCCESS", "splits": {k: len(v) for k, v in ds_math.items()}}
    except Exception as e:
        print(f"competition_math failed: {e}")
        results["competition_math"] = {"status": "FAILED", "error": str(e)}

    print("Results:", results)

if __name__ == "__main__":
    test_v14_candidates()
