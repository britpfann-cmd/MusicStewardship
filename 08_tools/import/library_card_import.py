"""MusicStewardship — D-side Library Card exchange importer prototype.

Rev A public encoding:
* CSV is the Library Card data artifact.
* 0..n and 1..n fields are compact JSON arrays in one CSV cell.
* 1 fields are scalar CSV values.
* D records its own processing revision.

The workbook test package remains supported as a convenience wrapper.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from typing import Any
D_PROCESSING_REVISION="library_card_import.revA-test"
JSON_ARRAY_FIELDS={"title","artist","orchestra_or_album_artist","singer","recording_identifier","recording_date","genre","style","source_album","composer","conductor","filename_numeric_component","filename_leading_text_candidate","sequence_number_candidate","source_suffix","source_grouping_label","source_context","evidence_summary","residual_evidence","conflicts","c_lineage"}
FIELD_DEFINITIONS=[
("card_revision","1","Library Card revision"),("library_card_interface_revision","1","Public exchange contract revision"),("c_processing_revision","1","C processing revision"),("source_object_id","1","Stable source-object identity"),("source_object_key","1","Source asset key"),("source_record_revision","1","C source-record schema revision"),("source_root","1","Supplied source boundary"),("relative_path","1","Source-relative asset path"),("filename","1","Original source filename"),("extension","0..1","Source filename extension"),("entry_type","1","Source object type"),("title","0..n","Initial catalog title"),("artist","0..n","Initial artist/performance attribution"),("orchestra_or_album_artist","0..n","Initial ensemble/album-artist value"),("singer","0..n","Initial singer value"),("recording_identifier","0..n","Initial recording identifier"),("recording_date","0..n","Initial recording date/year"),("genre","0..n","Initial genre"),("style","0..n","Initial style"),("source_album","0..n","Source album/release description"),("composer","0..n","Initial composer"),("conductor","0..n","Initial conductor"),("filename_numeric_component","0..n","Filename numeric component(s)"),("filename_leading_text_candidate","0..n","Leading filename text"),("sequence_number_candidate","0..n","Candidate sequence number"),("source_suffix","0..n","Terminal filename suffix"),("source_grouping_label","0..n","Source grouping label"),("source_context","0..n","Source contextual interpretation"),("evidence_summary","0..n","Compact native evidence summary"),("residual_evidence","0..n","Preserved uninterpreted evidence"),("construction_status","1","C construction status"),("conflicts","0..n","C-detected construction conflicts"),("c_lineage","1..n","C lineage references")]

def read_csv_table(path:Path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def rows_from_workbook(path:Path,sheet:str):
    import openpyxl; wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    if sheet not in wb.sheetnames: raise ValueError(f"Required sheet not found: {sheet}")
    return [list(r) for r in wb[sheet].iter_rows(values_only=True)]
def table_from_workbook(path:Path,sheet:str):
    data=rows_from_workbook(path,sheet)
    if not data: raise ValueError(f"{sheet} is empty")
    headers=["" if x is None else str(x) for x in data[0]]; out=[]
    for row in data[1:]:
        if not any(x not in (None,"") for x in row): continue
        out.append({headers[i]:"" if i>=len(row) or row[i] is None else str(row[i]) for i in range(len(headers))})
    return out
def package_info(path:Path):
    result={}
    for row in rows_from_workbook(path,"Package Info"):
        if len(row)>=2 and row[0] is not None: result[str(row[0])]="" if row[1] is None else str(row[1])
    return result
def decode_public_value(field,value):
    if value=="": return [] if field in JSON_ARRAY_FIELDS else ""
    if field in JSON_ARRAY_FIELDS:
        try: decoded=json.loads(value)
        except json.JSONDecodeError as exc: raise ValueError(f"Field {field!r} must contain a JSON array in Rev A.") from exc
        if not isinstance(decoded,list): raise ValueError(f"Field {field!r} must contain a JSON array in Rev A.")
        return decoded
    return value
def decode_card(card): return {field:decode_public_value(field,value) for field,value in card.items()}
def verify_standard(card):
    result=[]
    for field,cardinality,meaning in FIELD_DEFINITIONS:
        required=cardinality in ("1","1..n")
        if field not in card: result.append((field,"FAIL","Field absent from Library Card header.")); continue
        if required and card[field]=="": result.append((field,"REVIEW","Required field is present but blank.")); continue
        try: decoded=decode_public_value(field,card[field])
        except ValueError as exc: result.append((field,"FAIL",str(exc))); continue
        if cardinality in ("0..n","1..n") and not isinstance(decoded,list): result.append((field,"FAIL","Multi-valued field is not encoded as a JSON array."))
        else: result.append((field,"PASS",f"Represented: {meaning}"))
    return result
def verify_semantics(card):
    try: decoded=decode_card(card)
    except ValueError as exc:return [("semantic_decode","FAIL",str(exc))]
    checks=[
    ("filename_numeric_component",decoded.get("filename_numeric_component")==["01"],"01 remains a filename numeric component."),
    ("filename_leading_text_candidate",decoded.get("filename_leading_text_candidate")==["Track"],"Track remains filename leading text."),
    ("source_grouping_label",decoded.get("source_grouping_label")==["TANDA CALO BERON"],"Grouping label remains source_grouping_label."),
    ("source_context",decoded.get("source_context")==["MUSICA CIUDADANA","1 - TANGOS","CALO MIGUEL"],"Directory context survives the exchange as ordered values."),
    ("construction_status",decoded.get("construction_status")=="candidate","C construction status survives and remains distinct from D authority."),
    ("source_object_id",bool(decoded.get("source_object_id")),"Stable source-object identity is present."),
    ("c_processing_revision",decoded.get("c_processing_revision")=="source_record_builder.v1+library_card_exporter.revA-test","C processing revision is distinct from interface revision and source-record schema.")]
    return [(name,"PASS" if ok else "FAIL",detail) for name,ok,detail in checks]
def import_csv(cards_csv):
    cards=read_csv_table(cards_csv)
    if not cards: raise ValueError("No Library Card records found.")
    imported=[]; checks=[]
    for card in cards:
        imported_card=decode_card(card); imported_card["d_processing_revision"]=D_PROCESSING_REVISION; imported_card["d_import_interface_revision"]=card.get("library_card_interface_revision",""); imported.append(imported_card)
        checks += verify_standard(card); checks += verify_semantics(card)
    return cards,imported,checks
def import_workbook(workbook):
    info=package_info(workbook)
    if info.get("Interface revision")!="A": raise ValueError("This prototype expects Library Card interface revision A.")
    cards=table_from_workbook(workbook,"Library Cards")
    if not cards: raise ValueError("No Library Card records found.")
    imported=[]; checks=[]
    for card in cards:
        imported_card=decode_card(card); imported_card["d_processing_revision"]=D_PROCESSING_REVISION; imported_card["d_import_interface_revision"]=info["Interface revision"]; imported.append(imported_card)
        checks += verify_standard(card); checks += verify_semantics(card)
    return cards,imported,checks
def write_outputs(outdir,interface_revision,imported,checks):
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"D_imported_library_cards.json").write_text(json.dumps({"schema":"musicstewardship.d_imported_library_card.revA-test","d_processing_revision":D_PROCESSING_REVISION,"library_card_interface_revision":interface_revision,"records":imported},indent=2,ensure_ascii=False),encoding="utf-8")
    with (outdir/"D_verification.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["check","result","detail"]); w.writerows(checks)
    print(f"Interface revision   : {interface_revision}"); print(f"D processing revision: {D_PROCESSING_REVISION}"); print(f"Cards imported       : {len(imported)}"); print(f"Verification checks  : {len(checks)}"); print(f"PASS                 : {sum(r[1]=='PASS' for r in checks)}"); print(f"REVIEW               : {sum(r[1]=='REVIEW' for r in checks)}"); print(f"FAIL                 : {sum(r[1]=='FAIL' for r in checks)}"); print(f"Output               : {outdir}")
def main():
    ap=argparse.ArgumentParser(); source=ap.add_mutually_exclusive_group(required=True); source.add_argument("--csv",type=Path); source.add_argument("--workbook",type=Path); ap.add_argument("--output-dir",type=Path,required=True); args=ap.parse_args()
    if args.csv: _,imported,checks=import_csv(args.csv); interface_revision=imported[0].get("library_card_interface_revision","") if imported else ""
    else: info=package_info(args.workbook); _,imported,checks=import_workbook(args.workbook); interface_revision=info.get("Interface revision","")
    if interface_revision!="A": raise ValueError(f"Unsupported Library Card interface revision: {interface_revision!r}")
    write_outputs(args.output_dir,interface_revision,imported,checks)
if __name__=="__main__": main()
