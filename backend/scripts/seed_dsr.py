"""DSR data seed script — extracts items from DSR PDFs into the database.

Usage:
    python scripts/seed_dsr.py

This script populates the dsr_items table with:
- item_number, chapter, official_description, measurement_unit (from PDF)
- Empty knowledge fields (to be populated via Admin Panel)

Idempotent: runs upsert on item_number.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─── Sample DSR Data ───
# Since we can't parse the actual PDFs in this seed script reliably
# (PDF table extraction requires manual tuning per document),
# we provide a curated sample dataset covering major DSR chapters.
# The Admin Panel should be used to add/edit items going forward.

SAMPLE_DSR_DATA = [
    # Chapter 1: Earth Work
    {
        "item_number": "1.1",
        "chapter": "Earth Work",
        "official_description": "Earthwork in excavation by mechanical means (Hydraulic excavator) / manual means in foundation trenches or drains (not exceeding 1.5m in width or 10 sqm on plan), including dressing of sides and ramming of bottoms, lift upto 1.5m, including getting out the excavated soil and disposal of surplus excavated soil as directed, within a lead of 50m.",
        "simple_title": "Foundation Excavation",
        "summary": "Digging trenches for building foundations using machines or manual labor, up to 1.5m deep. Includes cleaning sides, compacting bottom, and moving excess soil within 50m.",
        "purpose": "To create trenches for laying building foundations, drainage systems, or underground utilities.",
        "where_used": ["Foundations", "Drainage", "Underground utilities", "Basements"],
        "materials": [],
        "execution_steps": [
            "Mark the layout as per drawing",
            "Set up bench marks for depth control",
            "Excavate using hydraulic excavator or manual means",
            "Dress the sides to maintain proper slope",
            "Ram the bottom for compaction",
            "Dispose surplus soil within 50m lead"
        ],
        "common_mistakes": [
            "Not checking soil bearing capacity before excavation",
            "Over-excavation beyond required depth",
            "Not maintaining proper side slopes",
            "Ignoring water table level"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 2",
        "search_keywords": ["excavation", "earth work", "foundation", "trenches", "digging"],
    },
    {
        "item_number": "1.2",
        "chapter": "Earth Work",
        "official_description": "Earthwork in excavation by mechanical means (Hydraulic excavator) / manual means over areas (exceeding 30cm in depth, 1.5m in width as well as 10sqm on plan) including disposal of excavated earth, lead upto 50m and lift upto 1.5m, disposed earth to be levelled and neatly dressed.",
        "simple_title": "Open Area Excavation",
        "summary": "Large area excavation exceeding 30cm depth and 1.5m width, including disposal and levelling of excavated earth within 50m lead.",
        "purpose": "For large-scale site levelling, basement excavation, or open foundation work.",
        "where_used": ["Site levelling", "Basement construction", "Open foundations", "Road cutting"],
        "materials": [],
        "execution_steps": [
            "Survey and mark excavation boundaries",
            "Establish depth benchmarks",
            "Excavate in layers using machines",
            "Transport excavated material to disposal area within 50m",
            "Level and dress the disposed earth",
            "Verify final levels against drawing"
        ],
        "common_mistakes": [
            "Not accounting for soil swell factor",
            "Excavating in rain-soaked conditions",
            "Poor disposal leading to site obstruction"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 2",
        "search_keywords": ["excavation", "open area", "site levelling", "earth cutting"],
    },
    # Chapter 4: Concrete Work
    {
        "item_number": "4.1",
        "chapter": "Concrete Work",
        "official_description": "Providing and laying in position cement concrete of specified grade excluding the cost of centering and shuttering - All work up to plinth level. 1:1.5:3 (1 Cement : 1.5 coarse sand : 3 graded stone aggregate 20mm nominal size).",
        "simple_title": "M20 Cement Concrete (Plinth Level)",
        "summary": "Mixing and placing M20 grade concrete (1:1.5:3 ratio) for work below plinth level. Does not include formwork cost.",
        "purpose": "To provide structural concrete for foundations, footings, and plinth beams.",
        "where_used": ["Foundations", "Footings", "Plinth beams", "Grade slabs"],
        "materials": [
            {"name": "OPC Cement 43 Grade", "quantity": "8.22 bags/cum"},
            {"name": "Coarse Sand", "quantity": "0.45 cum/cum"},
            {"name": "Stone Aggregate 20mm", "quantity": "0.90 cum/cum"},
            {"name": "Water", "quantity": "As required"}
        ],
        "execution_steps": [
            "Prepare formwork and check levels",
            "Ensure reinforcement is in position (if applicable)",
            "Batch concrete as per mix design 1:1.5:3",
            "Place concrete in layers not exceeding 150mm",
            "Vibrate using needle vibrator",
            "Level and finish the top surface",
            "Start curing after initial setting (6-8 hours)",
            "Continue curing for minimum 7 days"
        ],
        "common_mistakes": [
            "Adding excess water to improve workability",
            "Not vibrating concrete properly",
            "Inadequate curing period",
            "Concrete segregation during placement",
            "Not checking aggregate gradation"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 5.2",
        "search_keywords": ["concrete", "M20", "cement concrete", "plinth", "1:1.5:3", "foundation concrete"],
    },
    {
        "item_number": "4.1.1",
        "chapter": "Concrete Work",
        "official_description": "Providing and laying in position cement concrete of specified grade excluding the cost of centering and shuttering - All work up to plinth level. 1:2:4 (1 Cement : 2 coarse sand : 4 graded stone aggregate 20mm nominal size).",
        "simple_title": "M15 Cement Concrete (Plinth Level)",
        "summary": "M15 grade concrete (1:2:4 ratio) for plinth-level structural work and general foundations.",
        "purpose": "For bedding concrete, lean concrete, and general sub-structure work.",
        "where_used": ["PCC bedding", "Lean concrete", "Floor base"],
        "materials": [
            {"name": "OPC Cement 43 Grade", "quantity": "6.24 bags/cum"},
            {"name": "Coarse Sand", "quantity": "0.48 cum/cum"},
            {"name": "Stone Aggregate 20mm", "quantity": "0.96 cum/cum"}
        ],
        "execution_steps": [
            "Prepare the sub-base and compact",
            "Set formwork and check levels",
            "Batch concrete in 1:2:4 ratio",
            "Place and level concrete",
            "Cure for minimum 7 days"
        ],
        "common_mistakes": [
            "Using M15 where M20 or higher is specified",
            "Skipping compaction of sub-base",
            "Insufficient curing"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 5.2",
        "search_keywords": ["concrete", "M15", "PCC", "lean concrete", "1:2:4", "bedding"],
    },
    # Chapter 5: RCC Work
    {
        "item_number": "5.1",
        "chapter": "Reinforced Concrete Work",
        "official_description": "Providing and laying in position specified grade of reinforced cement concrete, excluding the cost of centering, shuttering, finishing and reinforcement - All work up to plinth level. 1:1.5:3 (1 Cement : 1.5 coarse sand (zone-III) : 3 graded stone aggregate 20mm nominal size).",
        "simple_title": "RCC M20 (Plinth Level)",
        "summary": "Reinforced cement concrete M20 grade for structural elements at plinth level. Excludes formwork and steel costs.",
        "purpose": "For constructing reinforced structural members like beams, columns, and slabs at foundation level.",
        "where_used": ["RCC footings", "Plinth beams", "Raft foundations", "Retaining walls"],
        "materials": [
            {"name": "OPC Cement 43 Grade", "quantity": "8.22 bags/cum"},
            {"name": "Coarse Sand (Zone-III)", "quantity": "0.45 cum/cum"},
            {"name": "Stone Aggregate 20mm", "quantity": "0.90 cum/cum"},
            {"name": "Water", "quantity": "As per W/C ratio"}
        ],
        "execution_steps": [
            "Check and approve reinforcement placement",
            "Ensure adequate cover to reinforcement",
            "Prepare concrete as per mix design",
            "Pour concrete and vibrate thoroughly",
            "Finish surface as specified",
            "Cure for minimum 14 days for structural members"
        ],
        "common_mistakes": [
            "Inadequate cover to reinforcement bars",
            "Cold joints due to delayed pouring",
            "Honeycombing from poor vibration",
            "Not using spacers for maintaining cover"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 5.5",
        "search_keywords": ["RCC", "reinforced concrete", "M20", "structural", "plinth"],
    },
    {
        "item_number": "5.9",
        "chapter": "Reinforced Concrete Work",
        "official_description": "Steel reinforcement for R.C.C work including straightening, cutting, bending, placing in position and binding all complete upto plinth level. Thermo-Mechanically Treated bars of grade Fe-500D or more.",
        "simple_title": "TMT Steel Reinforcement (Fe-500D)",
        "summary": "Providing and fixing TMT steel bars (Fe-500D grade) for RCC work, including all cutting, bending, and tying.",
        "purpose": "To provide tensile strength to concrete structural members.",
        "where_used": ["All RCC members", "Beams", "Columns", "Slabs", "Foundations"],
        "materials": [
            {"name": "TMT Bars Fe-500D", "quantity": "As per structural drawing"},
            {"name": "Binding Wire", "quantity": "8-10 kg per tonne of steel"}
        ],
        "execution_steps": [
            "Check bar bending schedule against structural drawings",
            "Straighten and cut bars to required lengths",
            "Bend bars as per BBS using bar bending machine",
            "Place reinforcement in position with spacers",
            "Tie bars securely with binding wire",
            "Get approval from engineer before concreting"
        ],
        "common_mistakes": [
            "Wrong bar diameter or spacing",
            "Insufficient lap length",
            "Not providing adequate development length",
            "Bent bars not as per BBS",
            "Missing stirrups at beam-column junctions"
        ],
        "measurement_unit": "Kg",
        "specification_reference": "CPWD Specifications Vol-1, Clause 5.12",
        "search_keywords": ["steel", "reinforcement", "TMT", "Fe-500D", "rebar", "bar bending"],
    },
    # Chapter 7: Brick Work
    {
        "item_number": "7.1",
        "chapter": "Brick Work",
        "official_description": "Brick work with common burnt clay F.P.S. (non modular) bricks of class designation 7.5 in foundation and plinth in: Cement mortar 1:6 (1 cement : 6 coarse sand).",
        "simple_title": "Brick Work in CM 1:6 (Foundation)",
        "summary": "Building brick walls in foundation and plinth using class 7.5 burnt clay bricks with cement mortar 1:6.",
        "purpose": "To construct load-bearing or partition walls in the foundation and plinth area.",
        "where_used": ["Foundation walls", "Plinth walls", "Boundary walls", "Retaining walls"],
        "materials": [
            {"name": "Burnt Clay Bricks (Class 7.5)", "quantity": "500 nos/cum"},
            {"name": "Cement", "quantity": "1.24 bags/cum"},
            {"name": "Coarse Sand", "quantity": "0.30 cum/cum"}
        ],
        "execution_steps": [
            "Soak bricks in water for minimum 2 hours",
            "Prepare cement mortar 1:6",
            "Lay bricks in English bond or as specified",
            "Maintain plumbness and alignment",
            "Ensure proper filling of joints",
            "Rake joints for plastering if required",
            "Cure brick work for minimum 7 days"
        ],
        "common_mistakes": [
            "Using dry bricks (absorbs moisture from mortar)",
            "Thick mortar joints exceeding 10mm",
            "Not maintaining proper bond pattern",
            "Vertical joints aligning in successive courses",
            "Insufficient curing"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 4",
        "search_keywords": ["brick work", "masonry", "CM 1:6", "foundation brick", "FPS bricks"],
    },
    {
        "item_number": "7.1.2",
        "chapter": "Brick Work",
        "official_description": "Brick work with common burnt clay F.P.S. (non modular) bricks of class designation 7.5 in superstructure above plinth level up to floor V level in: Cement mortar 1:4 (1 cement : 4 coarse sand).",
        "simple_title": "Brick Work in CM 1:4 (Superstructure)",
        "summary": "Brick masonry in superstructure (above plinth, up to 5th floor) using CM 1:4 for stronger bonding.",
        "purpose": "For constructing walls above plinth level where higher mortar strength is needed.",
        "where_used": ["External walls", "Internal walls", "Parapet walls", "Staircase walls"],
        "materials": [
            {"name": "Burnt Clay Bricks (Class 7.5)", "quantity": "500 nos/cum"},
            {"name": "Cement", "quantity": "1.72 bags/cum"},
            {"name": "Coarse Sand", "quantity": "0.28 cum/cum"}
        ],
        "execution_steps": [
            "Soak bricks thoroughly",
            "Prepare CM 1:4 mortar",
            "Lay bricks in specified bond pattern",
            "Check plumb and level every 3 courses",
            "Provide toothing where walls join later",
            "Leave openings for doors and windows as per drawing",
            "Cure for 10-14 days"
        ],
        "common_mistakes": [
            "Not providing proper toothing at junctions",
            "Not leaving chases for services",
            "Exceeding the daily height limit (1.5m/day)"
        ],
        "measurement_unit": "Cum",
        "specification_reference": "CPWD Specifications Vol-1, Clause 4.3",
        "search_keywords": ["brick work", "superstructure", "CM 1:4", "masonry above plinth"],
    },
    # Chapter 9: Plastering
    {
        "item_number": "9.44",
        "chapter": "Plastering",
        "official_description": "12mm cement plaster of mix 1:6 (1 cement: 6 fine sand).",
        "simple_title": "12mm Cement Plaster 1:6",
        "summary": "Applying 12mm thick cement plaster in 1:6 ratio to walls and ceilings for a smooth, even finish.",
        "purpose": "To provide a smooth protective coating on brick or concrete surfaces.",
        "where_used": ["Internal walls", "Ceilings", "External walls (with waterproofing)"],
        "materials": [
            {"name": "Cement", "quantity": "0.16 bags/sqm"},
            {"name": "Fine Sand", "quantity": "0.02 cum/sqm"},
            {"name": "Water", "quantity": "As required"}
        ],
        "execution_steps": [
            "Clean the surface and remove loose material",
            "Wet the surface thoroughly",
            "Apply spatterdash coat (cement slurry) if needed",
            "Fix dots and screeds for thickness control",
            "Apply mortar between screeds and level",
            "Finish surface with wooden float and steel trowel",
            "Cure for minimum 7 days"
        ],
        "common_mistakes": [
            "Plastering on dry surface",
            "Uneven thickness",
            "Cracks due to excess cement",
            "Not providing chicken mesh at dissimilar material junctions"
        ],
        "measurement_unit": "Sqm",
        "specification_reference": "CPWD Specifications Vol-2, Clause 6",
        "search_keywords": ["plaster", "cement plaster", "12mm", "1:6", "wall finishing", "plastering"],
    },
    # Chapter 12: Steel Work
    {
        "item_number": "12.1.1",
        "chapter": "Steel Work",
        "official_description": "Providing and fixing in position structural steel work in built-up sections, including cutting, hoisting, fixing in position and applying a priming coat of approved steel primer all complete.",
        "simple_title": "Structural Steel Work (Built-up Sections)",
        "summary": "Fabricating and installing structural steel members from built-up sections, including cutting, welding, erection, and primer coating.",
        "purpose": "For constructing steel structures, trusses, girders, and portal frames.",
        "where_used": ["Roof trusses", "Steel frames", "Girders", "Industrial structures"],
        "materials": [
            {"name": "Structural Steel Sections", "quantity": "As per drawing"},
            {"name": "Welding Electrodes", "quantity": "5-6% of steel weight"},
            {"name": "Steel Primer Paint", "quantity": "0.8-1.0 litre/sqm"}
        ],
        "execution_steps": [
            "Study structural drawings and prepare cutting plan",
            "Cut members to required dimensions",
            "Prepare and weld connections",
            "Trial assemble on ground if possible",
            "Hoist and fix in position using cranes",
            "Bolt or weld permanent connections",
            "Apply primer coat to all surfaces",
            "Get welding tested as per specification"
        ],
        "common_mistakes": [
            "Incorrect weld sizes",
            "Not removing mill scale before priming",
            "Poor alignment during erection",
            "Inadequate bracing during erection"
        ],
        "measurement_unit": "Kg",
        "specification_reference": "CPWD Specifications Vol-3, Clause 10",
        "search_keywords": ["steel work", "structural steel", "fabrication", "erection", "trusses"],
    },
    # Chapter 13: Painting
    {
        "item_number": "13.8",
        "chapter": "Painting",
        "official_description": "Finishing walls with Premium Acrylic Smooth exterior paint of required shade to give protective and decorative finish to concrete/cement plaster/ite surface as per manufacturer's specification.",
        "simple_title": "Exterior Acrylic Paint",
        "summary": "Applying premium acrylic exterior paint on plastered walls for weather protection and decorative finish.",
        "purpose": "To protect external walls from weather and give an aesthetic finish.",
        "where_used": ["External walls", "Boundary walls", "Building facades"],
        "materials": [
            {"name": "Exterior Primer", "quantity": "0.08 litre/sqm per coat"},
            {"name": "Acrylic Exterior Paint", "quantity": "0.13 litre/sqm per coat"}
        ],
        "execution_steps": [
            "Prepare surface — fill cracks and holes",
            "Sand the surface smooth",
            "Apply primer coat and allow to dry (4-6 hours)",
            "Apply first coat of exterior paint",
            "Allow drying time as per manufacturer's specs",
            "Apply second coat of paint",
            "Final inspection for coverage and consistency"
        ],
        "common_mistakes": [
            "Painting on damp surface",
            "Skipping primer coat",
            "Not maintaining wet edge while painting",
            "Insufficient drying time between coats"
        ],
        "measurement_unit": "Sqm",
        "specification_reference": "CPWD Specifications Vol-2, Clause 12",
        "search_keywords": ["painting", "exterior paint", "acrylic", "wall paint", "finishing"],
    },
    # Chapter 14: Flooring
    {
        "item_number": "14.37",
        "chapter": "Flooring",
        "official_description": "Providing and laying vitrified floor tiles of size 600x600mm (with joint width of 2mm to 3mm) of approved make, fixed with cement mortar 1:3 (1 cement : 3 coarse sand), including pointing the joints with white cement and pigment to match the shade of tiles.",
        "simple_title": "600x600mm Vitrified Floor Tiles",
        "summary": "Installing 600x600mm vitrified tiles with cement mortar bedding and matching joint pointing.",
        "purpose": "To provide a durable, water-resistant, and aesthetically pleasing floor finish.",
        "where_used": ["Living rooms", "Corridors", "Office spaces", "Commercial buildings"],
        "materials": [
            {"name": "Vitrified Tiles 600x600mm", "quantity": "1.05 sqm/sqm (incl. wastage)"},
            {"name": "Cement", "quantity": "0.32 bags/sqm"},
            {"name": "Coarse Sand", "quantity": "0.04 cum/sqm"},
            {"name": "White Cement", "quantity": "0.03 bags/sqm"}
        ],
        "execution_steps": [
            "Level and compact the base",
            "Prepare cement mortar 1:3 bedding (25-30mm thick)",
            "Soak tiles if required (check manufacturer instructions)",
            "Lay tiles with spacers maintaining 2-3mm joints",
            "Tap tiles to ensure full mortar contact",
            "Remove excess mortar from joints",
            "Point joints with white cement after 24 hours",
            "Cure and protect for 48 hours before foot traffic"
        ],
        "common_mistakes": [
            "Uneven bedding causing hollow tiles",
            "Not using spacers causing uneven joints",
            "Walking on tiles before mortar sets",
            "Not checking tile planarity before laying"
        ],
        "measurement_unit": "Sqm",
        "specification_reference": "CPWD Specifications Vol-2, Clause 11",
        "search_keywords": ["flooring", "vitrified tiles", "floor tiles", "600x600", "tile work"],
    },
]


async def seed_dsr_items() -> None:
    """Seed the database with DSR items."""
    from app.models.base import async_session_factory, init_db
    from app.repositories.dsr_repository import DSRRepository

    # Initialize database
    await init_db()

    async with async_session_factory() as session:
        repo = DSRRepository(session)
        created = 0
        updated = 0

        for data in SAMPLE_DSR_DATA:
            existing = await repo.get_by_item_number(data["item_number"])
            if existing:
                await repo.update(existing, data)
                updated += 1
                print(f"  Updated: {data['item_number']} — {data['simple_title']}")
            else:
                from app.models.dsr_item import DSRItem
                item = DSRItem(**data)
                await repo.create(item)
                created += 1
                print(f"  Created: {data['item_number']} — {data['simple_title']}")

        await session.commit()

    print(f"\nSeed complete: {created} created, {updated} updated")
    print(f"Total items in seed: {len(SAMPLE_DSR_DATA)}")


if __name__ == "__main__":
    print("Seeding DSR items...")
    asyncio.run(seed_dsr_items())
