"""Public capability catalog, checked against Lumnus's flip-card details on 2026-11-25."""
SOURCE='https://lumnusconsulting.net/services'
CHECKED='2026-11-25'
CATEGORIES={
 'Technology': ['Data and Business Analytics','Data Visualization','Business Intelligence','Data Strategy Development','Website Development'],
 'Industry Research':['Risk Assessment','Primary/Secondary Research','Consumer Surveys','Market Reports','Industry Overviews'],
 'Business Development':['Pricing Strategy','Revenue Modeling','Product Development','Sales Strategy','Cost Estimation Modeling'],
 'Business Strategy':['Business Model Development','Go-to-Market Strategy','Competitive Intelligence','Growth Strategy'],
 'Social Media & Marketing':['Brand Development','Marketing Strategy','Social Media Strategy','Graphic Design']}
SERVICES={name.lower().replace('/',' ').replace('&','and').replace(' ','_'):{'name':name,'category':cat,'technical':cat=='Technology','source':SOURCE} for cat,names in CATEGORIES.items() for name in names}
TECH={k for k,v in SERVICES.items() if v['technical']}

def capability_sentence(ids):
 names=[SERVICES[k]['name'].lower() for k in ids[:2]]
 return 'Lumnus’s published services include '+' and '.join(names)+'.'
