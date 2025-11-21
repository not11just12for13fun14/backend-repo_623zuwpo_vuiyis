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

    # 1) Special Power of Attorney (SPA)
    LegalTemplate(
        key="special_power_of_attorney",
        title="Special Power of Attorney",
        category="Affidavits / SPA",
        description="Authorizes an Attorney-in-Fact to act on specific matters.",
        questions=[
            {"key": "principal_name", "label": "Principal's Full Name", "type": "text"},
            {"key": "principal_civil_status", "label": "Principal Civil Status", "type": "select", "options": [
                {"label": "Single", "value": "Single"},
                {"label": "Married", "value": "Married"},
                {"label": "Widowed", "value": "Widowed"},
                {"label": "Separated", "value": "Separated"}
            ]},
            {"key": "principal_citizenship", "label": "Principal Citizenship", "type": "text", "placeholder": "Filipino"},
            {"key": "principal_address", "label": "Principal Address", "type": "textarea"},
            {"key": "agent_name", "label": "Attorney-in-Fact Full Name", "type": "text"},
            {"key": "agent_address", "label": "Attorney-in-Fact Address", "type": "textarea"},
            {"key": "powers", "label": "Specific Powers Granted", "type": "textarea", "placeholder": "e.g., to sell/manage a property, sign documents, receive payments"},
            {"key": "validity", "label": "Validity/Limitations", "type": "textarea", "placeholder": "e.g., valid for six (6) months from date of execution"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "SPECIAL POWER OF ATTORNEY\n\n"
            "KNOW ALL MEN BY THESE PRESENTS:\n\n"
            "I, {{principal_name}}, of legal age, {{principal_civil_status}}, {{principal_citizenship}}, and a resident of {{principal_address}}, do hereby NAME, CONSTITUTE and APPOINT {{agent_name}}, of legal age, and a resident of {{agent_address}}, as my true and lawful ATTORNEY-IN-FACT, to do and perform the following acts and deeds in my name, place and stead:\n\n"
            "{{powers}}\n\n"
            "This authority shall be {{validity}}.\n\n"
            "IN WITNESS WHEREOF, I have hereunto set my hand this {{date}} at {{city}}, Philippines.\n\n"
            "Principal: {{principal_name}}\n"
            "Attorney-in-Fact: {{agent_name}}\n"
        ),
        acknowledgement=(
            "BEFORE ME, a Notary Public for and in {{city}}, this {{date}}, personally appeared {{principal_name}} who is known to me and who acknowledged to me that the foregoing instrument is his/her free act and deed.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),

    # 2) Affidavit of Support and Consent
    LegalTemplate(
        key="affidavit_of_support_and_consent",
        title="Affidavit of Support and Consent",
        category="Affidavits",
        description="Affiant undertakes financial support and gives consent (often for minors/passport/travel).",
        questions=[
            {"key": "affiant_name", "label": "Affiant Full Name", "type": "text"},
            {"key": "affiant_civil_status", "label": "Civil Status", "type": "select", "options": [
                {"label": "Single", "value": "Single"},
                {"label": "Married", "value": "Married"},
                {"label": "Widowed", "value": "Widowed"},
                {"label": "Separated", "value": "Separated"}
            ]},
            {"key": "affiant_citizenship", "label": "Citizenship", "type": "text", "placeholder": "Filipino"},
            {"key": "affiant_address", "label": "Address", "type": "textarea"},
            {"key": "beneficiary_name", "label": "Beneficiary/Minor Name", "type": "text"},
            {"key": "relationship", "label": "Relationship to Beneficiary", "type": "text", "placeholder": "Parent/Guardian"},
            {"key": "purpose", "label": "Purpose of Support/Consent", "type": "textarea", "placeholder": "e.g., travel, passport application, schooling"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "AFFIDAVIT OF SUPPORT AND CONSENT\n\n"
            "I, {{affiant_name}}, of legal age, {{affiant_civil_status}}, {{affiant_citizenship}}, and a resident of {{affiant_address}}, after having been duly sworn in accordance with law, depose and state that:\n\n"
            "1. That I am the {{relationship}} of {{beneficiary_name}};\n"
            "2. That I hereby undertake to provide financial support as may be necessary;\n"
            "3. That I likewise give my full consent for the purpose of {{purpose}};\n"
            "4. That I am executing this affidavit to attest to the truth of the foregoing.\n\n"
            "IN WITNESS WHEREOF, I have hereunto set my hand this {{date}} in {{city}}, Philippines.\n\n"
            "Affiant: {{affiant_name}}\n"
        ),
        acknowledgement=(
            "SUBSCRIBED AND SWORN to before me this {{date}} in {{city}}, Philippines, affiant exhibited to me competent evidence of identity.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),

    # 3) Affidavit of Discrepancy
    LegalTemplate(
        key="affidavit_of_discrepancy",
        title="Affidavit of Discrepancy",
        category="Affidavits",
        description="Explains discrepancies in names or entries across records.",
        questions=[
            {"key": "affiant_name", "label": "Affiant Full Name", "type": "text"},
            {"key": "civil_status", "label": "Civil Status", "type": "select", "options": [
                {"label": "Single", "value": "Single"},
                {"label": "Married", "value": "Married"},
                {"label": "Widowed", "value": "Widowed"},
                {"label": "Separated", "value": "Separated"}
            ]},
            {"key": "citizenship", "label": "Citizenship", "type": "text", "placeholder": "Filipino"},
            {"key": "address", "label": "Address", "type": "textarea"},
            {"key": "correct_entry", "label": "Correct Entry (Name/Date/etc.)", "type": "text"},
            {"key": "erroneous_entry", "label": "Erroneous Entry as Appearing", "type": "text"},
            {"key": "record_type", "label": "Record Type", "type": "text", "placeholder": "e.g., Birth Certificate"},
            {"key": "agency", "label": "Issuing Agency/Office", "type": "text", "placeholder": "e.g., PSA"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "AFFIDAVIT OF DISCREPANCY\n\n"
            "I, {{affiant_name}}, of legal age, {{civil_status}}, {{citizenship}}, and a resident of {{address}}, after being duly sworn in accordance with law, depose and state:\n\n"
            "1. That there exists a discrepancy in my {{record_type}} issued by {{agency}};\n"
            "2. That the correct entry should be: {{correct_entry}}, but it appears as: {{erroneous_entry}};\n"
            "3. That this affidavit is executed to explain and rectify said discrepancy.\n\n"
            "IN WITNESS WHEREOF, I have hereunto set my hand this {{date}} at {{city}}, Philippines.\n\n"
            "Affiant: {{affiant_name}}\n"
        ),
        acknowledgement=(
            "SUBSCRIBED AND SWORN to before me this {{date}} in {{city}}, Philippines, affiant exhibited competent evidence of identity.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),

    # 4) Promissory Note
    LegalTemplate(
        key="promissory_note",
        title="Promissory Note",
        category="Contracts",
        description="Promise to pay a sum under specified terms.",
        questions=[
            {"key": "debtor_name", "label": "Debtor Name", "type": "text"},
            {"key": "debtor_address", "label": "Debtor Address", "type": "textarea"},
            {"key": "creditor_name", "label": "Creditor Name", "type": "text"},
            {"key": "amount", "label": "Principal Amount (PHP)", "type": "number"},
            {"key": "interest", "label": "Interest Rate (% per annum)", "type": "number", "placeholder": "e.g., 12"},
            {"key": "due_date", "label": "Due Date", "type": "date"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date of Execution", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "PROMISSORY NOTE\n\n"
            "For value received, I, {{debtor_name}}, residing at {{debtor_address}}, hereby promise to pay {{creditor_name}} the sum of Philippine Pesos: {{amount}}, with interest at the rate of {{interest}}% per annum, payable on or before {{due_date}}.\n\n"
            "In case of default, the undersigned agrees to pay attorney's fees and costs as may be allowed by law.\n\n"
            "IN WITNESS WHEREOF, I have set my hand this {{date}} at {{city}}, Philippines.\n\n"
            "Debtor: {{debtor_name}}\n"
        ),
        acknowledgement=(
            "ACKNOWLEDGED before me this {{date}} in {{city}}, Philippines by {{debtor_name}}, who is known to me and who executed the foregoing instrument.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),

    # 5) Residential Lease Agreement (Simple)
    LegalTemplate(
        key="lease_agreement_residential",
        title="Residential Lease Agreement",
        category="Contracts",
        description="Simple lease for residential property.",
        questions=[
            {"key": "lessor_name", "label": "Lessor (Landlord) Name", "type": "text"},
            {"key": "lessor_address", "label": "Lessor Address", "type": "textarea"},
            {"key": "lessee_name", "label": "Lessee (Tenant) Name", "type": "text"},
            {"key": "lessee_address", "label": "Lessee Address", "type": "textarea"},
            {"key": "property_address", "label": "Leased Premises Address", "type": "textarea"},
            {"key": "term_months", "label": "Lease Term (months)", "type": "number"},
            {"key": "monthly_rent", "label": "Monthly Rent (PHP)", "type": "number"},
            {"key": "deposit", "label": "Security Deposit (PHP)", "type": "number"},
            {"key": "advance", "label": "Advance Rent (PHP)", "type": "number"},
            {"key": "start_date", "label": "Start Date", "type": "date"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "RESIDENTIAL LEASE AGREEMENT\n\n"
            "This Lease Agreement is made this {{date}} in {{city}}, Philippines, by and between {{lessor_name}} (LESSOR), residing at {{lessor_address}}, and {{lessee_name}} (LESSEE), residing at {{lessee_address}}.\n\n"
            "1. Premises: {{property_address}}\n"
            "2. Term: {{term_months}} months commencing on {{start_date}}\n"
            "3. Rent: PHP {{monthly_rent}} per month, payable in advance every first day of the month\n"
            "4. Deposits: Security Deposit PHP {{deposit}}; Advance Rent PHP {{advance}}\n"
            "5. Utilities and maintenance for the account of the LESSEE unless otherwise agreed.\n\n"
            "IN WITNESS WHEREOF, the parties have hereunto set their hands on the date and place first above written.\n\n"
            "LESSOR: {{lessor_name}}\n"
            "LESSEE: {{lessee_name}}\n"
        ),
        acknowledgement=(
            "BEFORE ME, a Notary Public for and in {{city}}, this {{date}}, personally appeared {{lessor_name}} and {{lessee_name}} who acknowledged to me that the foregoing instrument is their free act and deed.\n\n"
            "Doc. No. ______; Page No. ______; Book No. ______; Series of 20___."
        ),
        requires_notarization=True,
        jurisdiction="Republic of the Philippines",
    ),

    # 6) Parental Consent for a Minor to Travel
    LegalTemplate(
        key="consent_to_travel_minor",
        title="Parental Consent for Minor to Travel",
        category="Affidavits",
        description="Allows a minor child to travel with consent of parent/guardian.",
        questions=[
            {"key": "parent_name", "label": "Parent/Guardian Name", "type": "text"},
            {"key": "parent_address", "label": "Parent Address", "type": "textarea"},
            {"key": "minor_name", "label": "Minor's Full Name", "type": "text"},
            {"key": "minor_birthdate", "label": "Minor's Birthdate", "type": "date"},
            {"key": "companion_name", "label": "Companion/Guardian During Travel", "type": "text"},
            {"key": "destination", "label": "Destination", "type": "text"},
            {"key": "travel_dates", "label": "Travel Dates / Duration", "type": "text"},
            {"key": "purpose", "label": "Purpose of Travel", "type": "textarea"},
            {"key": "city", "label": "City/Municipality", "type": "text"},
            {"key": "date", "label": "Date", "type": "date"}
        ],
        content=(
            "Republic of the Philippines\n\n"
            "PARENTAL CONSENT FOR MINOR TO TRAVEL\n\n"
            "I, {{parent_name}}, of legal age and residing at {{parent_address}}, hereby give my full consent for my minor child {{minor_name}} (born on {{minor_birthdate}}) to travel to {{destination}} on {{travel_dates}} under the care and supervision of {{companion_name}} for the purpose of {{purpose}}.\n\n"
            "I assume full responsibility for the foregoing consent.\n\n"
            "IN WITNESS WHEREOF, I have hereunto set my hand this {{date}} at {{city}}, Philippines.\n\n"
            "Parent/Guardian: {{parent_name}}\n"
        ),
        acknowledgement=(
            "SUBSCRIBED AND SWORN to before me this {{date}} in {{city}}, Philippines, affiant exhibited competent evidence of identity.\n\n"
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
