import os
from fpdf import FPDF

os.makedirs("docs", exist_ok=True)

class ComprehensiveAgriPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(2, 54, 37)  # Primary Green
        self.cell(0, 8, 'AnnaDATA Comprehensive Agronomic Knowledge Base & Policy Compendium', border=False, ln=True, align='C')
        self.set_draw_color(219, 218, 214)
        self.line(10, 18, 200, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(113, 121, 115)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(2, 54, 37)
        self.set_fill_color(239, 238, 234)
        self.cell(0, 8, title, ln=True, fill=True, border=False)
        self.ln(2)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(151, 71, 35)  # Secondary Rust/Brown
        self.cell(0, 6, title, ln=True)
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(27, 28, 26)
        self.multi_cell(0, 5.2, text.strip())
        self.ln(3)

pdf = ComprehensiveAgriPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ==========================================
# CHAPTER 1: CROP AGRONOMY & PACKAGES OF PRACTICES
# ==========================================
pdf.chapter_title("1. Comprehensive Crop Agronomy & Packages of Practices")

pdf.section_title("1.1 Paddy / Rice (Oryza sativa)")
pdf.body_text("""
- Agro-Climatic Requirements: Mean temperature 22°C to 34°C; annual rainfall 1200-2000 mm. Thrives in heavy clay, clay loam, and alluvial soils with pH 5.5 to 7.0.
- Sowing & Seed Rates: Direct Seeded Rice (DSR): 25-30 kg/ha; Nursery Transplanting: 40-50 kg/ha; System of Rice Intensification (SRI): 5-7 kg/ha.
- Spacing & Nursery: Transplant 21-25 day old seedlings at 20 cm x 15 cm spacing (2-3 seedlings per hill) or 25 cm x 25 cm for SRI (single seedling per hill).
- Fertilizer Schedule (NPK): Irrigated high-yielding varieties require 100-120:50-60:50-60 kg NPK/ha. Apply 25% N, 100% P2O5, and 50% K2O as basal dose during final puddle. Top dress remaining N in two equal splits at active tillering (20-25 DAT) and panicle initiation (40-45 DAT). Top dress remaining 50% K2O at panicle initiation.
- Zinc Deficiency Management: Apply 25 kg/ha Zinc Sulphate (ZnSO4 21%) as basal application. If foliar symptoms (Khaira disease / brown blotches) appear, spray 0.5% ZnSO4 + 1.0% Urea dissolved in water twice at 10-day intervals.
- High-Yielding Varieties (Eastern India & Odisha): OUAT Kalinga Rice-1 (Kolab - 130 days, 5.3 t/ha), Swarna (MTU 7029), Pooja, CR Dhan 310 (high protein), Sahbhagi Dhan (drought-tolerant), Lalat, Khandagiri.
""")

pdf.section_title("1.2 Sugarcane (Saccharum officinarum)")
pdf.body_text("""
- Soil & Climate: Deep well-drained loamy soils with pH 6.5 to 8.0. Requires 11-12 months of frost-free warm weather with 1500-2500 mm water.
- Planting Seasons: Autumn (Oct-Nov) gives 20-25% higher yield; Spring (Feb-March). Seed rate: 75,000 two-budded setts/ha or 50,000 three-budded setts/ha.
- Spacing & Furrows: Row-to-row spacing 90 cm to 120 cm. Trench planting recommended for mechanized harvesting and water conservation.
- Fertilizer Regimen: 250 kg N, 100 kg P2O5, 60-80 kg K2O per hectare. Apply entire P2O5 and 50% K2O in planting furrows. Apply Nitrogen in 3 splits: 25% at planting, 50% at tillering (45-60 DAP), and 25% during grand growth / earthing-up (90-120 DAP).
- Earthing Up & Propping: Carry out partial earthing up at 45 days and full earthing up at 90-100 days to prevent lodging and suppress late tillers.
- Varieties: Co-0238 (Karan 4 - high sucrose), Co-86032 (Nayana), Co-0118, Co-6907.
""")

pdf.section_title("1.3 Maize / Corn (Zea mays)")
pdf.body_text("""
- Seasons: Kharif (June-July), Rabi (Oct-Nov), and Spring (Feb). Requires well-drained fertile loamy soil; highly sensitive to waterlogging.
- Seed Rate & Spacing: Hybrids: 18-20 kg/ha; Composites: 20-22 kg/ha. Plant at 60 cm x 20 cm spacing at 4-5 cm depth.
- Nutrition (NPK): 120-150 kg N, 60-75 kg P2O5, 40-50 kg K2O per hectare. Apply full P, full K, and 1/3rd N as basal. Top-dress 1/3rd N at knee-high stage (V6) and remaining 1/3rd N at tasseling/silking stage.
- Critical Irrigation Stages: Knee-high stage, Tasseling stage, Silking stage, and Early grain filling / milk stage.
""")

pdf.section_title("1.4 Pulses & Oilseeds (Mustard, Groundnut, Gram/Chickpea, Moong)")
pdf.body_text("""
- Mustard (Brassica juncea): Seed rate 4-5 kg/ha; spacing 30 cm x 10 cm. NPK: 60-80:40:40 kg/ha + 20-30 kg Sulphur/ha (critical for oil synthesis). Varieties: Pusa Mustard 25, Varuna, Pusa Bold.
- Groundnut (Arachis hypogaea): Seed rate 100-110 kg kernels/ha; spacing 30 cm x 10 cm. Apply 20:40:40 NPK kg/ha + 200 kg Gypsum/ha at flowering/pegging (35-40 DAS) for pod development and calcium mobilization.
- Gram / Chickpea (Cicer arietinum): Seed rate 65-75 kg/ha (Desi) or 100 kg/ha (Kabuli). Seed treatment with Rhizobium + PSB culture (5 g/kg seed). NPK: 20:50:20 kg/ha. Avoid excess Nitrogen to prevent vegetative overgrowth.
- Green Gram / Moong: Short duration (60-70 days). Ideal catch crop for crop rotation. Seed rate 15-20 kg/ha. Varieties: IPM-02-3, Virat, Pusa Vishal.
""")

pdf.section_title("1.5 Millets (Ragi, Bajra, Jowar - Nutri-Cereals)")
pdf.body_text("""
- Finger Millet / Ragi (Eleusine coracana): Highly climate resilient, drought tolerant, thrives in red sandy loams. Seed rate 5 kg/ha for transplanting, 10 kg/ha for broadcasting. NPK: 60:30:30 kg/ha. Varieties: GPU 28, OUAT Kalinga Ragi, ML-365.
- Pearl Millet / Bajra: Requires 250-500 mm rain. NPK: 80:40:40 kg/ha. Highly suited for arid and semi-arid zones.
""")

# ==========================================
# CHAPTER 2: INTEGRATED PEST & DISEASE MANAGEMENT (IPM)
# ==========================================
pdf.chapter_title("2. Integrated Pest, Disease & Weed Management (IPM Protocols)")

pdf.section_title("2.1 Paddy Pests & Pathogens")
pdf.body_text("""
- Yellow Stem Borer (Scirpophaga incertulas): Causes 'Dead Hearts' at vegetative stage and 'White Ears' at reproductive stage. 
  Control: Install Pheromone traps @ 8-10/ha for monitoring. Biological: Release Trichogramma japonicum @ 100,000/ha at 30, 37, and 44 DAT. Chemical: Cartap Hydrochloride 4G @ 25 kg/ha or Chlorantraniliprole 18.5% SC @ 150 ml/ha in 500L water.
- Brown Planthopper (BPH - Nilaparvata lugens): Causes 'Hopper Burn' in circular patches. 
  Management: Provide 'Alleyways' (formation of 30 cm skip paths every 2-3 meters) for aeration and sunlight penetration. Chemical: Spray Pymetrozine 50% WDG @ 300 g/ha, Triflumezopyrim 10% SC @ 235 ml/ha, or Dinotefuran 20% SG @ 200 g/ha directed at plant base. Avoid synthetic pyrethroids which cause BPH resurgence.
- Blast Disease (Magnaporthe oryzae): Diamond/spindle-shaped lesions with grey center and brown margins on leaves, neck blast causes panicle collapse. 
  Control: Foliar spray of Tricyclazole 75% WP @ 0.6 g/L or Kasugamycin 3% SL @ 2.5 ml/L or Isoprothiolane 40% EC @ 1.5 ml/L.
- Bacterial Leaf Blight (BLB - Xanthomonas oryzae): Wave-like yellow/white lesions starting from leaf tips moving downwards. 
  Control: Spray Streptocycline @ 1 g + Copper Oxychloride @ 30 g in 10 liters of water. Drain excess standing water and reduce Nitrogen application.
- False Smut (Ustilaginoidea virens): Grain transformation into velvety yellow-green spore balls.
  Control: Preventive spray of Propiconazole 25% EC (1 ml/L) or Copper Hydroxide 77% WP (2 g/L) at 50% boot leaf stage before panicle emergence.
""")

pdf.section_title("2.2 Sugarcane Pests & Diseases")
pdf.body_text("""
- Early Shoot Borer (Chilo infuscatellus): Attacks young shoots (1-3 months), causing central dead hearts. 
  Control: Soil application of Fipronil 0.3% G @ 25 kg/ha or Chlorantraniliprole 0.4% G @ 18.75 kg/ha at planting time in furrows.
- Red Rot (Colletotrichum falcatum): Known as cancer of sugarcane. Causes internal reddening with distinct white horizontal patches and sour alcoholic smell. 
  Control: Crop rotation for 2-3 years, sett treatment with Carbendazim 50% WP @ 1 g/L for 15 minutes or hot water treatment at 52°C for 30 minutes. Use resistant clones.
- Smut (Sporisorium scitamineum): Production of long black whip-like unbranched structures from the spindle. 
  Control: Rogue out diseased clumps inside plastic bags; spray Propiconazole 25% EC @ 1 ml/L.
""")

pdf.section_title("2.3 Maize Fall Armyworm (Spodoptera frugiperda)")
pdf.body_text("""
- Symptoms: Large ragged feeding holes on leaves, deep whorl damage with moist sawdust-like frass.
- Economic Threshold Level (ETL): 5% damaged plants at seedling to early whorl stage.
- Control Measures: Hand-pick egg masses; apply neem cake in whorls; foliar spray of Spinetoram 11.7% SC @ 0.5 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L or Chlorantraniliprole 18.5% SC @ 0.4 ml/L directly into the leaf whorls using knapsack sprayer.
""")

# ==========================================
# CHAPTER 3: SOIL HEALTH, NUTRIENT MANAGEMENT & BIOFERTILIZERS
# ==========================================
pdf.chapter_title("3. Soil Science, Fertility & Precision Nutrient Management")

pdf.section_title("3.1 Soil Testing & Interpretation Standards")
pdf.body_text("""
- Soil pH Range: Acidic (<6.0) - requires agricultural lime (CaCO3) or dolomite @ 2-4 t/ha; Neutral (6.5-7.5) - ideal for nutrient uptake; Alkaline / Sodic (>8.5) - requires Gypsum (CaSO4) application with flushing.
- Soil Organic Carbon (SOC): Low (<0.50%), Medium (0.50-0.75%), High (>0.75%). For soils with SOC < 0.5%, incorporate 5-10 t/ha Farm Yard Manure (FYM) or green manuring with Dhaincha (Sesbania aculeata) or Sunn hemp (Crotalaria juncea).
- Available Macronutrient Benchmarks:
  - Nitrogen (N): Low (<280 kg/ha), Medium (280-560 kg/ha), High (>560 kg/ha).
  - Phosphorus (P2O5): Low (<10 kg/ha), Medium (10-25 kg/ha), High (>25 kg/ha).
  - Potassium (K2O): Low (<110 kg/ha), Medium (110-280 kg/ha), High (>280 kg/ha).
""")

pdf.section_title("3.2 Micronutrient Deficiency Diagnosis & Correction")
pdf.body_text("""
- Zinc (Zn): Interveinal chlorosis on young leaves, bronze spots, stunted internodes. Correction: Soil application of ZnSO4 @ 25 kg/ha once in 2-3 seasons or foliar spray of 0.5% ZnSO4.
- Boron (B): Fruit cracking, hollow heart in cauliflower/potato, poor grain filling. Correction: Soil application of Borax @ 10 kg/ha or foliar spray of Solubor (0.1-0.2%).
- Iron (Fe): Complete whitening/bleaching of young leaves in calcareous or high-pH soils. Correction: Foliar spray of 1.0% Ferrous Sulphate (FeSO4) + 0.1% Citric Acid.
""")

pdf.section_title("3.3 Biofertilizers & Organic Consortia")
pdf.body_text("""
- Rhizobium: Symbiotic N-fixation for legumes; fixes 50-100 kg N/ha.
- Azotobacter & Azospirillum: Free-living/associative N-fixers for cereals, millets, sugarcane; fixes 20-40 kg N/ha and synthesizes IAA growth hormones.
- Phosphate Solubilizing Bacteria (PSB - Bacillus megaterium / Pseudomonas striata): Solubilizes insoluble tricalcium phosphate; saves 15-20% chemical phosphatic fertilizer.
- Vesicular Arbuscular Mycorrhiza (VAM / Glomus spp.): Enhances root surface area for phosphorus, zinc, and moisture uptake under water stress.
""")

# ==========================================
# CHAPTER 4: GOVERNMENT SCHEMES, SUBSIDIES & FARM ECONOMICS
# ==========================================
pdf.chapter_title("4. Government Schemes, Policy Subsidies & Agricultural Economics")

pdf.section_title("4.1 Central Government Agricultural Schemes")
pdf.body_text("""
- PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Direct income transfer of Rs 6,000 per year in three equal installments of Rs 2,000 directly into Aadhaar-linked bank accounts of landholding farmer families.
- PMFBY (Pradhan Mantri Fasal Bima Yojana): Comprehensive crop insurance coverage against non-preventable natural risks (drought, flood, pests, post-harvest losses). Premium paid by farmer: 2.0% of sum insured for Kharif food/oilseed crops, 1.5% for Rabi food/oilseed crops, and 5.0% for annual commercial/horticultural crops.
- PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan):
  - Component-B: Installation of standalone solar agriculture pumps. Subsidized up to 70% (30% Central Govt + 30-40% State Govt, remaining 30-40% farmer contribution or bank loan).
  - Component-C: Solarization of existing grid-connected agricultural pumps with net-metering option to sell excess power back to the grid.
- PMKSY - Per Drop More Crop (Micro Irrigation): Financial assistance for installation of Drip and Sprinkler irrigation systems: up to 55% subsidy for small and marginal farmers, and 45% subsidy for other categories.
- Soil Health Card Scheme: Periodic soil testing across 12 parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) issued to farmers every 2-3 years with crop-wise fertilizer recommendations.
""")

pdf.section_title("4.2 Odisha State Specific Schemes & Interventions")
pdf.body_text("""
- KALIA Scheme (Krushak Assistance for Livelihood and Income Augmentation): Financial support for small/marginal farmers and landless agricultural households in Odisha for input procurement and livelihood support.
- Odisha Millets Mission (OMM / Special Programme for Promotion of Millets in Tribal Areas): Comprehensive support covering Rs 26,000+ per hectare incentive over five years for millet cultivation, free quality seeds, community processing units, and guaranteed procurement at MSP.
- Mukhyamantri Krushi Udyog Yojana (MKUY): Capital Investment Subsidy (CIS) up to 40% (50% for SC/ST/Women/Graduates in Agriculture) up to Rs 50 Lakh for setting up commercial agri-enterprises and agro-processing units in Odisha.
- Balaram Scheme: Credit support for landless tenant farmers / sharecroppers through Joint Liability Groups (JLGs) via cooperative and commercial banks.
- SAFAL (Simplified Application for Agricultural Loans): Single-window portal for farmers and agri-entrepreneurs in Odisha to access 300+ financial products from 40+ banks.
""")

pdf.section_title("4.3 Minimum Support Price (MSP) & Mandi Operations")
pdf.body_text("""
- MSP Mandate: Recommended by CACP (Commission for Agricultural Costs and Prices) based on A2+FL formula (Actual paid-out costs + imputed value of unpaid Family Labor) ensuring minimum 50% profit margin over cost of production.
- Key Reference MSP Benchmarks:
  - Paddy (Common): Rs 2,300/quintal; Paddy (Grade A): Rs 2,320/quintal.
  - Maize: Rs 2,225/quintal.
  - Cotton (Medium Staple): Rs 7,121/quintal; Cotton (Long Staple): Rs 7,521/quintal.
  - Sugarcane (FRP - Fair & Remunerative Price): Rs 340/quintal linked to basic recovery rate of 10.25%.
  - Wheat: Rs 2,275 - 2,425/quintal.
  - Mustard / Rapeseed: Rs 5,650/quintal.
  - Gram (Chickpea): Rs 5,440/quintal.
- e-NAM (National Agriculture Market): Pan-India electronic trading portal networking existing APMC mandis to create a unified national market for agricultural commodities, enabling online bidding, digital weighing, and direct electronic settlement.
""")

# ==========================================
# CHAPTER 5: METEOROLOGY, WATER BUDGETING & DIGITAL TWIN TELEMETRY
# ==========================================
pdf.chapter_title("5. Meteorology, Irrigation Engineering & Digital Twin Telemetry")

pdf.section_title("5.1 Open-Meteo & Agronomic Telemetry Rules")
pdf.body_text("""
- Evapotranspiration (ET0 - FAO Penman-Monteith): Reference crop evapotranspiration indicates daily moisture loss. Crop Water Need (ETc) = ET0 x Kc (Crop Coefficient).
  - Paddy Kc values: Initial stage = 1.05, Mid-season = 1.20, Maturity = 0.90.
  - Sugarcane Kc values: Initial = 0.40, Grand Growth = 1.25, Maturity = 0.75.
- Spraying Window Decision Engine:
  - Wind Speed Rule: Wind speed between 3 km/h and 12 km/h is optimal for spraying. Wind speed > 15 km/h triggers Spray Drift Warning (chemical drift damage). Wind speed < 2 km/h during hot afternoons indicates thermal inversion risk.
  - Rain Forecast Rule: If precipitation probability > 60% within 4 hours, hold pesticide spraying (prevents chemical washoff).
  - Temperature & Relative Humidity (RH) Delta: RH > 85% with temperatures 24-28°C triggers high fungal sporulation risk (Blast / Sheath Blight alert).
""")

pdf.section_title("5.2 Micro-Irrigation & Water Conservation")
pdf.body_text("""
- Drip Irrigation Efficiency: 90-95% water use efficiency, delivers water directly to root zone, prevents weed growth between rows, enables Fertigation (dissolving water-soluble 19:19:19 or Urea directly in irrigation lines).
- Sprinkler Irrigation Efficiency: 75-85% efficiency, suitable for undulating terrain, closely spaced crops (groundnut, wheat, mustard, pulses). Avoid overhead sprinkling during flowering to prevent pollen wash.
- Water Budgeting in Paddy: Alternate Wetting and Drying (AWD) technique reduces irrigation water requirement by 25-30% and reduces methane emissions without yield penalty. Water is re-introduced when field water table drops to 15 cm below soil surface (monitored via perforated field tube).
""")

pdf.output("docs/annadata_knowledge.pdf")
print(" Successfully compiled master knowledge base: docs/annadata_knowledge.pdf")