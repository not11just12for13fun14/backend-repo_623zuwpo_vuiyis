import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import LegalTemplate, GeneratedDocument

app = FastAPI(title="PH Legal Document Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "PH Legal Document Generator API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------- Seed Templates (insert once if not present) ----------
DEFAULT_TEMPLATES: List[LegalTemplate] = [
    LegalTemplate(
        key="affidavit_of_loss",
        title="Affidavit of Loss",
        category="Affidavits",
        description="Used to declare the loss of an item such as an ID, license, or document.",
        questions=[
            {"key": "full_name", "label": "Full Name", "type": "text", "placeholder": "Juan Dela Cruz"},
            {"key": "civil_status", "label": "Civil Status", "type": "select", "options": [
                {"label": "Single", "value": "Single"},
                {"label": "Married", "value": "Married"},
                {"label": "Widowed", "value": "Widowed"},
                {"label": "Separated", "value": "Separated"}
            ]},
            {"key": "citizenship", "label": "Citizenship", "type": "text", "placeholder": "Filipino"},
            {"key": "address", "label": "Address", "type": "textarea"},
            {"key": "id_type", "label": "Gov't ID Presented", "type": "text", "placeholder": "Driver's License"},
            {"key": "id_number", "label": "ID Number", "type": "text"},
            {"key": "lost_item", "label": "Item Lost", "type": "text", "placeholder": "Company ID"},
            {"key": "place_lost", "label": "Place Lost", "type": "text"},
            {"key": "date_lost", "label": "Date Lost", "type": "date"},
            {"key": "circumstances", "label": "Circumstances of Loss", "type": "textarea"},
            {"key": "city", "label": "City/Municipality of Notarization", "type": "text", "placeholder": "Quezon City"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "AFFIDAVIT OF LOSS\n\n"
            "I, {{full_name}}, of legal age, {{civil_status}}, Filipino, and a resident of {{address}}, after having been duly sworn in accordance with law, do hereby depose and state that:\n\n"
            "1. That I am the lawful owner/holder of a {{lost_item}};\n"
            "2. That on or about {{date_lost}} at {{place_lost}}, the aforesaid item was lost under the following circumstances: {{circumstances}};\n"
            "3. That despite diligent efforts to locate the said item, the same could not be found;\n"
            "4. That I am executing this affidavit to attest to the truth of the foregoing and for whatever legal purpose it may serve.\n\n"
            "IN WITNESS WHEREOF, I have hereunto set my hand this ___ day of __________, 20___ at {{city}}, Philippines.\n\n"
            "Affiant: {{full_name}}\n"
            "ID Presented: {{id_type}} ({{id_number}})\n"
        ),
        acknowledgement=(
            "SUBSCRIBED AND SWORN to before me this ___ day of __________, 20___ in {{city}}, Philippines, affiant exhibited to me his/her competent evidence of identity indicated above.\n\n"
            "Doc. No. ______;\n"
            "Page No. ______;\n"
            "Book No. ______;\n"
            "Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),
    LegalTemplate(
        key="deed_of_absolute_sale",
        title="Deed of Absolute Sale",
        category="Contracts",
        description="Agreement for the sale of personal property between a seller and buyer.",
        questions=[
            {"key": "seller_name", "label": "Seller Name", "type": "text"},
            {"key": "seller_address", "label": "Seller Address", "type": "textarea"},
            {"key": "buyer_name", "label": "Buyer Name", "type": "text"},
            {"key": "buyer_address", "label": "Buyer Address", "type": "textarea"},
            {"key": "property_description", "label": "Property Description", "type": "textarea", "placeholder": "e.g., 2016 Toyota Vios (Engine No..., Plate No...)"},
            {"key": "sale_price", "label": "Purchase Price (PHP)", "type": "number"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date of Execution", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "DEED OF ABSOLUTE SALE\n\n"
            "KNOW ALL MEN BY THESE PRESENTS:\n\n"
            "This Deed made and executed on {{date}} at {{city}}, Philippines by and between \n"
            "{{seller_name}}, of legal age, Filipino, and with address at {{seller_address}} (the 'SELLER'), and \n"
            "{{buyer_name}}, of legal age, Filipino, and with address at {{buyer_address}} (the 'BUYER');\n\n"
            "WITNESSETH: That for and in consideration of the sum of Philippine Pesos: {{sale_price}}, the SELLER hereby sells, transfers and conveys unto the BUYER the following property:\n\n"
            "{{property_description}}\n\n"
            "The SELLER warrants that the property is free from all liens and encumbrances.\n\n"
            "IN WITNESS WHEREOF, the parties have hereunto set their hands this {{date}} at {{city}}, Philippines.\n\n"
            "SELLER: {{seller_name}}\n"
            "BUYER: {{buyer_name}}\n"
        ),
        acknowledgement=(
            "BEFORE ME, a Notary Public for and in {{city}}, Philippines, this {{date}}, personally appeared {{seller_name}} and {{buyer_name}} who are known to me and who executed the foregoing instrument and acknowledged that the same is their free act and deed.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),
]


def seed_templates_if_empty():
    # Only insert defaults if collection is empty
    existing = db["legaltemplate"].count_documents({}) if db else 0
    if existing == 0 and db is not None:
        for tpl in DEFAULT_TEMPLATES:
            create_document("legaltemplate", tpl)


@app.on_event("startup")
def on_startup():
    try:
        if db is not None:
            seed_templates_if_empty()
    except Exception:
        pass


# ---------- API Models ----------
class GenerateRequest(BaseModel):
    template_key: str
    answers: Dict[str, Any]
    as_html: bool = True


# ---------- Utilities ----------
import re

def render_template_text(template: str, answers: Dict[str, Any]) -> str:
    def repl(match):
        key = match.group(1)
        value = answers.get(key, f"{{{{{key}}}}}")
        return str(value)
    return re.sub(r"\{\{\s*([a-zA-Z0-9_\.\-]+)\s*\}\}", repl, template)


def text_to_html(text: str) -> str:
    # Simple conversion: preserve newlines and basic emphasis
    lines = text.split("\n")
    html_lines = [f"<p>{line}</p>" if line.strip() else "<br/>" for line in lines]
    return "\n".join(html_lines)


# ---------- Routes ----------
@app.get("/api/templates", response_model=List[LegalTemplate])
def list_templates():
    docs = get_documents("legaltemplate") if db is not None else []
    # Convert Mongo docs to Pydantic
    out: List[LegalTemplate] = []
    keys_seen = set()
    for d in docs:
        d.pop("_id", None)
        try:
            tpl = LegalTemplate(**d)
            # protect against duplicates
            if tpl.key not in keys_seen:
                out.append(tpl)
                keys_seen.add(tpl.key)
        except Exception:
            continue
    # If DB empty or unavailable, fall back to defaults (in-memory)
    if not out:
        out = DEFAULT_TEMPLATES
    return out


@app.post("/api/generate", response_model=GeneratedDocument)
def generate_document(req: GenerateRequest):
    # find template
    templates = list_templates()
    tpl = next((t for t in templates if t.key == req.template_key), None)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    rendered_text = render_template_text(tpl.content, req.answers)
    ack_text = render_template_text(tpl.acknowledgement or "", req.answers)

    full_text = rendered_text
    if ack_text.strip():
        full_text += "\n\n" + ack_text

    rendered_html = text_to_html(full_text) if req.as_html else None

    doc: GeneratedDocument = GeneratedDocument(
        template_key=tpl.key,
        answers=req.answers,
        rendered_text=full_text,
        rendered_html=rendered_html,
        title=tpl.title,
    )

    try:
        create_document("generateddocument", doc)
    except Exception:
        # ignore if DB not available
        pass

    return doc


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
