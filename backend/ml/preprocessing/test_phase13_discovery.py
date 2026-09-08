import sys
import json
import traceback

def test_sources():
    print("Testing source discovery...")
    import datasets
    
    results = {}
    
    # 1. SciQ
    try:
        print("Testing SciQ...")
        ds_sciq = datasets.load_dataset("sciq", trust_remote_code=True)
        counts = {k: len(v) for k, v in ds_sciq.items()}
        print(f"SciQ loaded: {counts}")
        results["sciq"] = {"status": "SUCCESS", "splits": counts}
    except Exception as e:
        print(f"SciQ failed: {e}")
        results["sciq"] = {"status": "FAILED", "error": str(e)}

    # 2. AI2 ARC
    try:
        print("Testing AI2 ARC...")
        ds_arc = datasets.load_dataset("allenai/ai2_arc", "ARC-Easy", trust_remote_code=True)
        counts_easy = {k: len(v) for k, v in ds_arc.items()}
        ds_arc_c = datasets.load_dataset("allenai/ai2_arc", "ARC-Challenge", trust_remote_code=True)
        counts_chal = {k: len(v) for k, v in ds_arc_c.items()}
        print(f"ARC Easy: {counts_easy}, ARC Challenge: {counts_chal}")
        results["ai2_arc"] = {"status": "SUCCESS", "ARC-Easy": counts_easy, "ARC-Challenge": counts_chal}
    except Exception as e:
        print(f"AI2 ARC failed: {e}")
        results["ai2_arc"] = {"status": "FAILED", "error": str(e)}

    # 3. ScienceQA
    try:
        print("Testing ScienceQA...")
        ds_sqa = datasets.load_dataset("derek-thomas/ScienceQA", trust_remote_code=True)
        counts_sqa = {k: len(v) for k, v in ds_sqa.items()}
        print(f"ScienceQA: {counts_sqa}")
        results["ScienceQA"] = {"status": "SUCCESS", "splits": counts_sqa}
    except Exception as e:
        print(f"ScienceQA failed: {e}")
        results["ScienceQA"] = {"status": "FAILED", "error": str(e)}

    # 4. MMLU (High School Physics / Chemistry / Biology / Math)
    try:
        print("Testing MMLU STEM subsets...")
        mmlu_subs = ["high_school_physics", "high_school_chemistry", "high_school_biology", "high_school_mathematics", "conceptual_physics"]
        mmlu_res = {}
        for sub in mmlu_subs:
            ds_m = datasets.load_dataset("cais/mmlu", sub, trust_remote_code=True)
            mmlu_res[sub] = {k: len(v) for k, v in ds_m.items()}
        print(f"MMLU STEM: {mmlu_res}")
        results["MMLU"] = {"status": "SUCCESS", "subsets": mmlu_res}
    except Exception as e:
        print(f"MMLU failed: {e}")
        results["MMLU"] = {"status": "FAILED", "error": str(e)}

    # 5. OpenBookQA
    try:
        print("Testing OpenBookQA...")
        ds_obqa = datasets.load_dataset("allenai/openbookqa", "main", trust_remote_code=True)
        counts_obqa = {k: len(v) for k, v in ds_obqa.items()}
        print(f"OpenBookQA: {counts_obqa}")
        results["openbookqa"] = {"status": "SUCCESS", "splits": counts_obqa}
    except Exception as e:
        print(f"OpenBookQA failed: {e}")
        results["openbookqa"] = {"status": "FAILED", "error": str(e)}

    with open(r"datasets\raw\v13\discovery_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Done testing!")

if __name__ == "__main__":
    test_sources()
