from tika import parser
import re
from collections import Counter

# ===== 1. CONFIGURATION =====

RESUME_PATH = ''

# Paste the job description here as a multi-line string
JOB_DESCRIPTION = """


"""

# Common English words to ignore (stop words)
STOP_WORDS = set("""
a an the and or but if then else for of in on at to from by with as is are was were
be been being have has had do does did will would shall should can could may might must
this that these those i you he she it we they me him her us them my your his its our their
not no yes also more most some any all each every other another such same so than too very
about into through during before after above below between within without across against
job role work team company candidate applicant position experience required preferred
plus bonus etc ability years year minimum maximum responsibilities qualifications skills
including ensure able strong excellent good great new our we you your
""".split())


# ===== 2. EXTRACT TEXT FROM RESUME =====

def extract_resume_text(path):
    parsed = parser.from_file(path)
    return parsed['content'] or ''


# ===== 3. TOKENIZATION (mimics ATS behavior) =====

def tokenize(text):
    """Lowercase, strip punctuation, split on whitespace — same as basic ATS."""
    text = text.lower()
    # Keep alphanumerics, dots (for .net, node.js), pluses (c++), hashes (c#), hyphens
    text = re.sub(r"[^\w\s\.\+\#\-/]", ' ', text)
    tokens = text.split()
    # Strip trailing punctuation but preserve internal
    tokens = [t.strip('.-/') for t in tokens]
    return [t for t in tokens if t and t not in STOP_WORDS and len(t) > 1]


def extract_phrases(text, max_n=3):
    """Extract 1-, 2-, and 3-word phrases (n-grams) for compound keyword matching."""
    tokens = tokenize(text)
    phrases = set(tokens)
    for n in range(2, max_n + 1):
        for i in range(len(tokens) - n + 1):
            phrases.add(' '.join(tokens[i:i + n]))
    return phrases


# ===== 4. KEYWORD EXTRACTION FROM JD =====

# Curated technical keyword dictionary — extend for your field
TECH_KEYWORDS = {
       # ========================================================================
    # PROGRAMMING LANGUAGES
    # ========================================================================
    'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'cpp',
    'go', 'golang', 'rust', 'ruby', 'php', 'perl', 'scala', 'kotlin', 'swift',
    'objective-c', 'r', 'matlab', 'julia', 'lua', 'dart', 'elixir', 'erlang',
    'haskell', 'clojure', 'f#', 'groovy', 'vb.net', 'visual basic', 'cobol',
    'fortran', 'assembly', 'solidity', 'crystal', 'nim', 'zig', 'ocaml',

    # Shell / scripting
    'bash', 'shell', 'shell scripting', 'zsh', 'powershell', 'batch', 'cmd',
    'awk', 'sed', 'tcl', 'expect',

    # Markup / data languages
    'html', 'html5', 'css', 'css3', 'html/css', 'sass', 'scss', 'less',
    'xml', 'json', 'yaml', 'toml', 'markdown', 'latex',

    # Query languages
    'sql', 'pl/sql', 'plsql', 't-sql', 'tsql', 'mysql', 'nosql', 'graphql',
    'sparql', 'cypher', 'hql', 'mdx',

    # ========================================================================
    # FRONTEND FRAMEWORKS / LIBRARIES
    # ========================================================================
    'react', 'reactjs', 'react.js', 'react native', 'next.js', 'nextjs',
    'vue', 'vue.js', 'vuejs', 'nuxt', 'nuxt.js', 'angular', 'angularjs',
    'svelte', 'sveltekit', 'ember', 'ember.js', 'backbone', 'backbone.js',
    'jquery', 'gatsby', 'remix', 'astro', 'solidjs', 'preact', 'lit',
    'redux', 'mobx', 'zustand', 'recoil', 'rxjs',
    'tailwind', 'tailwind css', 'bootstrap', 'material ui', 'mui',
    'chakra ui', 'ant design', 'styled components', 'emotion',
    'webpack', 'vite', 'rollup', 'parcel', 'esbuild', 'turbopack',
    'babel', 'eslint', 'prettier', 'storybook',

    # ========================================================================
    # BACKEND FRAMEWORKS
    # ========================================================================
    # Python
    'flask', 'django', 'fastapi', 'pyramid', 'tornado', 'bottle', 'falcon',
    'celery', 'sqlalchemy',
    # Node
    'node', 'nodejs', 'node.js', 'express', 'express.js', 'nestjs', 'koa',
    'hapi', 'fastify', 'meteor', 'sails',
    # Java
    'spring', 'spring boot', 'spring mvc', 'spring cloud', 'spring security',
    'hibernate', 'struts', 'jsf', 'jakarta ee', 'java ee', 'jpa', 'jdbc',
    'maven', 'gradle', 'ant',
    # Ruby
    'rails', 'ruby on rails', 'sinatra',
    # PHP
    'laravel', 'symfony', 'codeigniter', 'wordpress', 'drupal',
    # .NET
    '.net', 'dotnet', 'asp.net', 'asp.net core', '.net core', '.net framework',
    'entity framework', 'blazor', 'wpf', 'winforms', 'xamarin', 'maui',
    # Go
    'gin', 'echo', 'fiber', 'beego',
    # Rust
    'actix', 'rocket', 'axum', 'tokio',
    # Other
    'phoenix', 'play framework',

    # ========================================================================
    # MOBILE
    # ========================================================================
    'ios', 'android', 'swiftui', 'uikit', 'jetpack compose', 'kotlin multiplatform',
    'flutter', 'react native', 'ionic', 'cordova', 'capacitor', 'expo',
    'xcode', 'android studio',

    # ========================================================================
    # DATABASES — RELATIONAL
    # ========================================================================
    'postgresql', 'postgres', 'mysql', 'mariadb', 'sqlite',
    'microsoft sql server', 'mssql', 'sql server', 't-sql',
    'oracle', 'oracle db', 'oracle database', 'oracle ebs', 'oracle fusion',
    'oracle fusion cloud', 'oracle erp', 'oracle hcm', 'oracle epm',
    'hyperion', 'otbi', 'oic',
    'db2', 'ibm db2', 'sap hana', 'teradata', 'snowflake', 'redshift',
    'bigquery', 'cockroachdb', 'amazon rds', 'amazon aurora', 'azure sql',

    # ========================================================================
    # DATABASES — NOSQL / SPECIALIZED
    # ========================================================================
    'mongodb', 'redis', 'cassandra', 'dynamodb', 'couchdb', 'couchbase',
    'firebase', 'firestore', 'realm', 'elasticsearch', 'opensearch',
    'solr', 'lucene', 'neo4j', 'arangodb', 'orientdb', 'janusgraph',
    'influxdb', 'timescaledb', 'prometheus', 'graphite',
    'memcached', 'hazelcast', 'etcd', 'consul', 'zookeeper',

    # ========================================================================
    # ORM / DB TOOLS
    # ========================================================================
    'prisma', 'sequelize', 'typeorm', 'mongoose', 'knex', 'drizzle',
    'sqlalchemy', 'alembic', 'flyway', 'liquibase', 'dbt',
    'stored procedures', 'triggers', 'views', 'indexes', 'query optimization',
    'database design', 'data modeling', 'erd', 'normalization',

    # ========================================================================
    # CLOUD PLATFORMS
    # ========================================================================
    'aws', 'amazon web services', 'azure', 'microsoft azure',
    'gcp', 'google cloud', 'google cloud platform',
    'oracle cloud', 'oci', 'ibm cloud', 'alibaba cloud', 'digitalocean',
    'linode', 'heroku', 'vercel', 'netlify', 'render', 'fly.io', 'railway',
    'cloudflare', 'cloudflare workers',

    # AWS services
    'ec2', 's3', 'lambda', 'aws lambda', 'rds', 'aurora', 'dynamodb',
    'cloudfront', 'cloudwatch', 'iam', 'route53', 'route 53', 'vpc',
    'sns', 'sqs', 'kinesis', 'eks', 'ecs', 'fargate', 'elastic beanstalk',
    'cloudformation', 'sagemaker', 'glue', 'athena', 'emr', 'redshift',
    'api gateway', 'cognito', 'amplify', 'step functions', 'eventbridge',
    'secrets manager', 'parameter store', 'codepipeline', 'codebuild',
    'codedeploy', 'codecommit', 'security groups',

    # Azure services
    'azure devops', 'azure functions', 'azure blob storage', 'azure ad',
    'azure active directory', 'entra id', 'azure sql', 'cosmos db',
    'azure kubernetes service', 'aks', 'azure pipelines', 'app service',
    'logic apps', 'event hubs', 'service bus', 'application insights',
    'azure monitor', 'key vault',

    # GCP services
    'google compute engine', 'gce', 'google kubernetes engine', 'gke',
    'cloud functions', 'cloud run', 'cloud storage', 'pub/sub', 'dataflow',
    'dataproc', 'cloud spanner', 'firestore', 'app engine', 'vertex ai',

    # ========================================================================
    # DEVOPS / CI-CD / INFRASTRUCTURE
    # ========================================================================
    'docker', 'docker compose', 'kubernetes', 'k8s', 'helm', 'kustomize',
    'openshift', 'rancher', 'nomad', 'mesos', 'podman', 'containerd',
    'terraform', 'pulumi', 'ansible', 'puppet', 'chef', 'saltstack',
    'packer', 'vagrant',
    'jenkins', 'github actions', 'gitlab ci', 'gitlab ci/cd', 'circleci',
    'travis ci', 'bamboo', 'teamcity', 'argocd', 'argo cd', 'flux',
    'spinnaker', 'tekton', 'drone',
    'ci/cd', 'cicd', 'continuous integration', 'continuous deployment',
    'continuous delivery', 'devops', 'gitops', 'infrastructure as code', 'iac',
    'sre', 'site reliability engineering',
    'nginx', 'apache', 'apache http', 'httpd', 'iis', 'tomcat', 'jboss',
    'wildfly', 'caddy', 'traefik', 'haproxy', 'envoy', 'istio', 'linkerd',
    'service mesh',

    # ========================================================================
    # VERSION CONTROL
    # ========================================================================
    'git', 'github', 'gitlab', 'bitbucket', 'azure repos', 'gitea',
    'svn', 'subversion', 'mercurial', 'perforce', 'tfvc',
    'version control',

    # ========================================================================
    # OBSERVABILITY / MONITORING
    # ========================================================================
    'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk', 'elk stack',
    'elasticsearch', 'logstash', 'kibana', 'fluentd', 'fluent bit',
    'loki', 'tempo', 'jaeger', 'zipkin', 'opentelemetry', 'otel',
    'sentry', 'rollbar', 'bugsnag', 'pagerduty', 'opsgenie', 'victorops',
    'cloudwatch', 'azure monitor', 'stackdriver', 'app insights',
    'apm', 'observability', 'logging', 'monitoring', 'tracing', 'metrics',

    # ========================================================================
    # MESSAGING / STREAMING / EVENTS
    # ========================================================================
    'kafka', 'apache kafka', 'rabbitmq', 'activemq', 'pulsar', 'nats',
    'sqs', 'sns', 'kinesis', 'pub/sub', 'event hubs', 'service bus',
    'mqtt', 'amqp', 'event-driven', 'event driven',

    # ========================================================================
    # DATA ENGINEERING / BIG DATA / ETL
    # ========================================================================
    'hadoop', 'hdfs', 'mapreduce', 'spark', 'apache spark', 'pyspark',
    'flink', 'storm', 'beam', 'apache beam', 'hive', 'pig', 'oozie',
    'airflow', 'apache airflow', 'prefect', 'dagster', 'luigi',
    'dbt', 'fivetran', 'stitch', 'matillion', 'informatica', 'talend',
    'ssis', 'ssrs', 'ssas', 'data warehouse', 'data warehousing',
    'data lake', 'data lakehouse', 'lakehouse', 'delta lake', 'iceberg',
    'etl', 'elt', 'data pipeline', 'data engineering', 'data integration',
    'data modeling', 'dimensional modeling', 'star schema', 'snowflake schema',
    'olap', 'oltp', 'cdc', 'change data capture',

    # ========================================================================
    # MACHINE LEARNING / AI / DATA SCIENCE
    # ========================================================================
    'machine learning', 'ml', 'deep learning', 'artificial intelligence', 'ai',
    'neural networks', 'cnn', 'rnn', 'lstm', 'transformer', 'transformers',
    'nlp', 'natural language processing', 'computer vision', 'cv',
    'reinforcement learning', 'rl', 'supervised learning', 'unsupervised learning',
    'generative ai', 'genai', 'llm', 'large language models', 'rag',
    'fine-tuning', 'fine tuning', 'prompt engineering', 'embeddings',
    'vector database', 'vector db', 'pinecone', 'weaviate', 'chroma', 'qdrant',
    'milvus', 'faiss',

    # ML frameworks
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'xgboost',
    'lightgbm', 'catboost', 'jax', 'flax', 'huggingface', 'hugging face',
    'transformers', 'langchain', 'llamaindex', 'openai', 'anthropic',
    'mlflow', 'kubeflow', 'sagemaker', 'vertex ai', 'azure ml',
    'wandb', 'weights and biases', 'tensorboard', 'dvc',

    # Data analysis
    'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh',
    'jupyter', 'jupyter notebook', 'colab', 'google colab', 'databricks',
    'ipython', 'streamlit', 'gradio', 'dash',

    # Statistics
    'statistics', 'statistical analysis', 'regression', 'classification',
    'clustering', 'time series', 'a/b testing', 'hypothesis testing',
    'bayesian', 'monte carlo', 'feature engineering', 'feature selection',

    # ========================================================================
    # BUSINESS INTELLIGENCE / ANALYTICS / REPORTING
    # ========================================================================
    'powerbi', 'power bi', 'tableau', 'looker', 'qlik', 'qliksense',
    'qlikview', 'metabase', 'superset', 'apache superset', 'redash',
    'mode analytics', 'sigma', 'sisense', 'domo', 'thoughtspot',
    'cognos', 'microstrategy', 'sap businessobjects', 'crystal reports',
    'google analytics', 'mixpanel', 'amplitude', 'segment', 'heap',
    'hotjar', 'fullstory',

    # ========================================================================
    # APIS / WEB SERVICES / INTEGRATION
    # ========================================================================
    'rest', 'rest api', 'restful', 'restful api', 'soap', 'soap api',
    'graphql', 'grpc', 'web services', 'web service', 'api', 'apis',
    'api design', 'api gateway', 'openapi', 'swagger', 'postman', 'insomnia',
    'webhooks', 'oauth', 'oauth2', 'jwt', 'saml', 'openid connect', 'oidc',
    'microservices', 'monolith', 'monolithic', 'service-oriented architecture',
    'soa', 'event-driven architecture', 'serverless',
    'integration', 'system integration', 'enterprise integration',
    'api integration', 'third-party integrations',

    # ========================================================================
    # SECURITY / CYBERSECURITY
    # ========================================================================
    'cybersecurity', 'cyber security', 'information security', 'infosec',
    'application security', 'appsec', 'network security', 'cloud security',
    'devsecops', 'sast', 'dast', 'iast', 'sca', 'penetration testing',
    'pentesting', 'pen test', 'ethical hacking', 'red team', 'blue team',
    'vulnerability', 'vulnerability assessment', 'vulnerability management',
    'threat modeling', 'threat intelligence', 'incident response',
    'security incident', 'security audit', 'security awareness',
    'siem', 'soar', 'edr', 'xdr', 'mdr', 'dlp', 'casb', 'waf', 'ids', 'ips',
    'firewall', 'vpn', 'zero trust', 'mfa', 'multi-factor authentication',
    'sso', 'single sign-on', 'iam', 'identity and access management',
    'rbac', 'role-based access control', 'abac', 'attribute-based access control',
    'pki', 'tls', 'ssl', 'encryption', 'cryptography', 'hashing',
    'owasp', 'owasp top 10', 'cve', 'cvss', 'nvd',
    'compliance', 'soc 2', 'soc2', 'iso 27001', 'pci dss', 'hipaa', 'gdpr',
    'ccpa', 'sox', 'fedramp', 'nist', 'cis benchmarks',
    'crowdstrike', 'palo alto', 'fortinet', 'cisco', 'okta', 'auth0',
    'duo', 'cyberark', 'beyondtrust',

    # ========================================================================
    # NETWORKING
    # ========================================================================
    'tcp/ip', 'tcp', 'udp', 'http', 'https', 'http/2', 'http/3', 'dns',
    'dhcp', 'nat', 'subnetting', 'vlan', 'vpn', 'load balancing',
    'load balancer', 'cdn', 'reverse proxy', 'forward proxy',
    'osi model', 'firewalls', 'switches', 'routers', 'wifi', 'wireless',
    'lan', 'wan', 'wlan', 'bgp', 'ospf', 'mpls', 'sd-wan', 'sdn',
    'ccna', 'ccnp', 'comptia network+',

    # ========================================================================
    # OPERATING SYSTEMS
    # ========================================================================
    'linux', 'ubuntu', 'debian', 'centos', 'rhel', 'red hat', 'fedora',
    'arch linux', 'alpine', 'suse', 'unix', 'solaris', 'aix', 'freebsd',
    'macos', 'mac os', 'windows', 'windows server', 'windows 10', 'windows 11',
    'wsl', 'windows subsystem for linux',

    # ========================================================================
    # ENTERPRISE IT / INFRASTRUCTURE
    # ========================================================================
    'active directory', 'ad', 'azure active directory', 'azure ad', 'entra id',
    'group policy', 'group policies', 'gpo',
    'ldap', 'kerberos', 'radius', 'tacacs',
    'microsoft intune', 'intune', 'jamf', 'mdm', 'mam', 'sccm',
    'office 365', 'microsoft 365', 'm365', 'exchange', 'sharepoint',
    'teams', 'onedrive', 'outlook',
    'google workspace', 'g suite',
    'vmware', 'esxi', 'vsphere', 'vcenter', 'hyper-v', 'kvm', 'xen',
    'virtualization', 'hypervisor', 'virtual machines', 'vms',
    'citrix', 'rdp', 'vdi', 'thin client',
    'backup', 'disaster recovery', 'dr', 'business continuity', 'bcp',
    'high availability', 'ha', 'failover', 'redundancy',
    'storage', 'san', 'nas', 'iscsi', 'nfs', 'smb', 'cifs',

    # ========================================================================
    # ENTERPRISE APPLICATIONS / ERP / SAAS
    # ========================================================================
    'sap', 'sap hana', 'sap s/4hana', 'sap successfactors', 'sap ariba',
    'oracle fusion', 'oracle ebs', 'oracle erp cloud', 'oracle hcm cloud',
    'workday', 'peoplesoft', 'jd edwards', 'netsuite', 'sage',
    'microsoft dynamics', 'dynamics 365', 'dynamics ax', 'dynamics gp',
    'salesforce', 'sfdc', 'salesforce sales cloud', 'salesforce service cloud',
    'salesforce marketing cloud', 'apex', 'lightning', 'visualforce',
    'hubspot', 'marketo', 'pardot', 'mailchimp', 'sendgrid',
    'servicenow', 'jira', 'jira service management', 'confluence',
    'atlassian', 'bitbucket', 'trello', 'asana', 'monday.com', 'clickup',
    'sharepoint', 'documentum', 'box', 'dropbox',
    'zendesk', 'freshdesk', 'intercom', 'drift',
    'docusign', 'adobe sign',

    # ========================================================================
    # SERVICE DESK / IT SUPPORT / ITSM
    # ========================================================================
    'service desk', 'help desk', 'helpdesk', 'technical support',
    'desktop support', 'tier 1', 'tier 2', 'tier 3', 'l1', 'l2', 'l3',
    'incident management', 'problem management', 'change management',
    'release management', 'configuration management', 'knowledge management',
    'asset management', 'lifecycle management', 'hardware provisioning',
    'troubleshooting', 'remote support', 'remote desktop',
    'ticketing', 'ticketing system', 'sla', 'okr', 'kpi',
    'itil', 'itil 4', 'itil4', 'itsm', 'cobit',
    'sop', 'sops', 'standard operating procedures', 'runbook', 'runbooks',
    'playbook', 'knowledge base', 'kb article',

    # ========================================================================
    # DATABASE / DATA OPERATIONS
    # ========================================================================
    'database administration', 'dba', 'database administrator',
    'database design', 'database tuning', 'sql tuning', 'query optimization',
    'database patching', 'patch management', 'database security',
    'data integrity', 'data quality', 'data governance',
    'data migration', 'data conversion', 'data refresh', 'data import',
    'data export', 'replication', 'sharding', 'partitioning',
    'backup and recovery', 'point-in-time recovery', 'rpo', 'rto',
    'schema design', 'schema changes', 'schema migration',

    # ========================================================================
    # TESTING / QA
    # ========================================================================
    'unit testing', 'unit test', 'integration testing', 'integration test',
    'end-to-end testing', 'e2e testing', 'system testing', 'acceptance testing',
    'uat', 'user acceptance testing', 'regression testing', 'smoke testing',
    'performance testing', 'load testing', 'stress testing', 'security testing',
    'manual testing', 'automated testing', 'test automation', 'tdd', 'bdd',
    'jest', 'mocha', 'chai', 'jasmine', 'cypress', 'playwright', 'puppeteer',
    'selenium', 'webdriver', 'appium', 'testng', 'junit', 'pytest', 'unittest',
    'rspec', 'cucumber', 'postman', 'soapui', 'jmeter', 'gatling', 'k6', 'locust',
    'qa', 'quality assurance', 'qe', 'quality engineering',
    'test cases', 'test plans', 'acceptance criteria', 'bug tracking',

    # ========================================================================
    # METHODOLOGIES / PROCESS / PM
    # ========================================================================
    'agile', 'scrum', 'kanban', 'lean', 'xp', 'extreme programming',
    'safe', 'scaled agile framework', 'less', 'waterfall', 'rad',
    'sdlc', 'software development life cycle', 'software development lifecycle',
    'project management', 'program management', 'portfolio management',
    'product management', 'product owner', 'scrum master',
    'pmp', 'capm', 'prince2', 'six sigma', 'lean six sigma',
    'business analysis', 'business analyst', 'requirements gathering',
    'requirements analysis', 'use cases', 'user stories', 'epics',
    'sprint planning', 'sprint review', 'sprint retrospective', 'standup',
    'daily standup', 'backlog', 'backlog grooming',
    'change management', 'risk management', 'stakeholder management',
    'governance', 'compliance', 'audit', 'auditing',

    # ========================================================================
    # SOFTWARE ARCHITECTURE / DESIGN
    # ========================================================================
    'design patterns', 'mvc', 'mvvm', 'singleton', 'factory', 'observer',
    'decorator', 'strategy', 'adapter', 'facade', 'proxy', 'dependency injection',
    'solid principles', 'solid', 'clean code', 'clean architecture',
    'domain-driven design', 'ddd', 'event sourcing', 'cqrs',
    'object-oriented programming', 'oop', 'functional programming', 'fp',
    'reactive programming', 'concurrency', 'parallelism', 'multithreading',
    'asynchronous', 'async', 'await', 'promises', 'callbacks',
    'system design', 'distributed systems', 'high availability', 'scalability',
    'performance', 'optimization', 'caching', 'cdn',
    'microservices architecture', 'monolithic architecture', 'serverless architecture',

    # ========================================================================
    # COLLABORATION / PRODUCTIVITY TOOLS
    # ========================================================================
    'jira', 'confluence', 'slack', 'microsoft teams', 'zoom', 'webex',
    'github', 'gitlab', 'bitbucket', 'notion', 'coda', 'figma', 'sketch',
    'invision', 'miro', 'mural', 'lucidchart', 'visio', 'draw.io',
    'trello', 'asana', 'monday.com', 'clickup', 'basecamp', 'linear',

    # ========================================================================
    # SOFT SKILLS / GENERAL (sometimes filtered on)
    # ========================================================================
    'communication', 'leadership', 'teamwork', 'collaboration',
    'problem-solving', 'problem solving', 'critical thinking',
    'analytical', 'attention to detail', 'time management',
    'organization', 'mentoring', 'coaching', 'training',
    'cross-functional', 'cross functional',
    'stakeholder', 'stakeholders', 'customer-facing', 'customer service',
    'presentation', 'documentation', 'technical writing',

    # ========================================================================
    # CERTIFICATIONS (commonly searched)
    # ========================================================================
    'aws certified', 'aws solutions architect', 'aws sysops', 'aws developer',
    'aws devops engineer', 'aws security', 'aws machine learning',
    'azure fundamentals', 'az-900', 'azure administrator', 'az-104',
    'azure developer', 'az-204', 'azure solutions architect', 'az-305',
    'azure devops engineer', 'az-400', 'azure security engineer', 'az-500',
    'gcp associate', 'gcp professional',
    'cissp', 'ccsp', 'cism', 'cisa', 'ceh', 'oscp', 'security+', 'comptia security+',
    'network+', 'a+', 'comptia a+', 'linux+',
    'ccna', 'ccnp', 'ccie',
    'pmp', 'capm', 'csm', 'certified scrum master', 'cspo', 'safe',
    'itil 4', 'itil4 foundation', 'itil foundation',
    'oracle certified', 'ocp', 'oca',
    'mcsa', 'mcse', 'mcsd',
    'rhce', 'rhcsa',
    'cfa', 'cpa',

    # ========================================================================
    # EMERGING / SPECIALIZED
    # ========================================================================
    'blockchain', 'cryptocurrency', 'crypto', 'bitcoin', 'ethereum',
    'smart contracts', 'web3', 'defi', 'nft', 'dao',
    'iot', 'internet of things', 'embedded systems', 'edge computing',
    'arduino', 'raspberry pi', 'firmware', 'rtos',
    'ar', 'vr', 'xr', 'augmented reality', 'virtual reality',
    'unity', 'unreal engine', 'unreal', 'game development',
    'quantum computing', 'qiskit',
    'robotics', 'ros', 'robot operating system',

    # ========================================================================
    # FINANCE / DOMAIN-SPECIFIC TECH
    # ========================================================================
    'fix protocol', 'bloomberg', 'reuters', 'murex', 'calypso',
    'algorithmic trading', 'quantitative analysis', 'risk modeling',
    'fraud detection', 'aml', 'kyc',
    'epic', 'cerner', 'meditech', 'hl7', 'fhir', 'dicom',

}


def extract_jd_keywords(jd_text):
    """Find which known tech keywords appear in the JD."""
    jd_phrases = extract_phrases(jd_text, max_n=3)
    found = set()
    for kw in TECH_KEYWORDS:
        if kw in jd_phrases:
            found.add(kw)
    return found


def find_must_haves(jd_text, all_keywords):
    """Heuristic: keywords mentioned near 'required', 'must', 'minimum'."""
    must_haves = set()
    sentences = re.split(r'[.\n]', jd_text.lower())
    trigger_words = ['required', 'must have', 'must-have', 'minimum',
                     'requirements', 'essential', 'mandatory']
    for sentence in sentences:
        if any(t in sentence for t in trigger_words):
            for kw in all_keywords:
                if kw in sentence:
                    must_haves.add(kw)
    return must_haves



NEAR_MISS_HINTS = {

    # ========================================================================
    # VERSION CONTROL
    # ========================================================================
    'git':                     ['github', 'gitlab', 'bitbucket'],
    'github':                  ['git', 'gitlab'],
    'gitlab':                  ['git', 'github'],
    'version control':         ['git', 'github', 'gitlab', 'svn', 'mercurial', 'bitbucket'],
    'svn':                     ['subversion', 'version control'],
    'subversion':              ['svn', 'version control'],

    # ========================================================================
    # LANGUAGES — short/ambiguous ones especially
    # ========================================================================
    'javascript':              ['js', 'ecmascript', 'es6', 'typescript', 'node.js', 'react'],
    'typescript':              ['ts', 'javascript'],
    'js':                      ['javascript'],
    'ts':                      ['typescript'],
    'python':                  ['py', 'python3', 'python 3', 'flask', 'django', 'fastapi'],
    'java':                    ['jvm', 'spring', 'spring boot', 'jakarta', 'java ee'],
    'go':                      ['golang', 'go programming', 'go language'],
    'golang':                  ['go', 'go programming', 'go language'],
    'c++':                     ['cpp', 'c plus plus'],
    'cpp':                     ['c++'],
    'c#':                      ['csharp', 'c sharp', '.net', 'dotnet'],
    'csharp':                  ['c#'],
    '.net':                    ['dotnet', 'c#', 'asp.net', '.net core', '.net framework'],
    'dotnet':                  ['.net'],
    'kotlin':                  ['android', 'jvm'],
    'swift':                   ['ios', 'swiftui', 'objective-c'],
    'objective-c':             ['ios', 'swift'],
    'ruby':                    ['rails', 'ruby on rails'],
    'php':                     ['laravel', 'symfony', 'wordpress'],
    'rust':                    ['cargo', 'rustc'],
    'scala':                   ['jvm', 'akka', 'spark'],
    'r':                       ['r programming', 'rstudio', 'r language'],
    'matlab':                  ['octave'],
    'shell':                   ['bash', 'zsh', 'shell scripting'],
    'bash':                    ['shell', 'shell scripting', 'zsh'],
    'powershell':              ['ps1', 'pwsh', 'shell scripting'],

    # ========================================================================
    # NODE / RUNTIMES
    # ========================================================================
    'nodejs':                  ['node.js', 'node js', 'node', 'express', 'nestjs','nodeJS'],
    'node.js':                 ['nodejs', 'node js', 'node','nodeJS'],
    'node':                    ['nodejs', 'node.js'],
    'deno':                    ['nodejs', 'javascript runtime'],
    'bun':                     ['nodejs', 'javascript runtime'],

    # ========================================================================
    # FRONTEND
    # ========================================================================
    'react':                   ['reactjs', 'react.js', 'react native', 'next.js'],
    'reactjs':                 ['react', 'react.js'],
    'react.js':                ['react', 'reactjs'],
    'next.js':                 ['nextjs', 'next', 'react'],
    'nextjs':                  ['next.js', 'next', 'react'],
    'vue':                     ['vue.js', 'vuejs', 'nuxt'],
    'vue.js':                  ['vue', 'vuejs'],
    'angular':                 ['angularjs', 'angular.js', 'typescript'],
    'frontend':                ['front-end', 'front end', 'react', 'vue', 'angular', 'html', 'css', 'javascript', 'ui'],
    'front-end':               ['frontend', 'front end'],
    'front end':               ['frontend', 'front-end'],
    'ui':                      ['user interface', 'frontend', 'react', 'vue', 'angular'],
    'ux':                      ['user experience', 'ui/ux', 'design'],
    'css':                     ['sass', 'scss', 'less', 'tailwind', 'styling'],
    'sass':                    ['scss', 'css'],
    'tailwind':                ['tailwind css', 'css'],

    # ========================================================================
    # BACKEND
    # ========================================================================
    'backend':                 ['back-end', 'back end', 'flask', 'django', 'spring boot', 'express', 'nodejs', 'fastapi', 'rails', 'laravel', '.net', 'server-side'],
    'back-end':                ['backend', 'back end'],
    'back end':                ['backend', 'back-end'],
    'server-side':             ['backend', 'server side'],
    'server side':             ['backend', 'server-side'],
    'flask':                   ['python', 'rest api', 'web framework'],
    'django':                  ['python', 'rest api', 'web framework'],
    'fastapi':                 ['python', 'rest api', 'web framework'],
    'spring':                  ['java', 'spring boot', 'spring framework'],
    'spring boot':             ['java', 'spring', 'rest api'],
    'express':                 ['nodejs', 'node.js', 'rest api'],
    'rails':                   ['ruby on rails', 'ruby'],
    'laravel':                 ['php'],
    'asp.net':                 ['.net', 'c#', 'dotnet'],

    # ========================================================================
    # APIS / WEB SERVICES
    # ========================================================================
    'api':                     ['apis', 'rest api', 'rest', 'restful', 'graphql', 'soap', 'web service', 'web services', 'flask', 'spring boot', 'express'],
    'apis':                    ['api', 'rest api', 'restful'],
    'rest':                    ['rest api', 'restful', 'restful api', 'rest services', 'web services'],
    'rest api':                ['rest', 'restful', 'api', 'web services'],
    'restful':                 ['rest', 'rest api', 'restful api'],
    'soap':                    ['soap api', 'soap services', 'web services', 'wsdl'],
    'graphql':                 ['gql', 'apollo', 'api'],
    'grpc':                    ['protobuf', 'protocol buffers', 'rpc'],
    'web services':            ['rest', 'rest api', 'soap', 'api', 'apis', 'wsdl'],
    'web service':             ['web services', 'api', 'rest', 'soap'],
    'webhooks':                ['callbacks', 'event-driven'],

    # ========================================================================
    # DATABASES
    # ========================================================================
    'sql':                     ['mysql', 'postgresql', 'sql server', 'mssql', 'oracle', 'sqlite', 'pl/sql', 't-sql'],
    'nosql':                   ['mongodb', 'cassandra', 'dynamodb', 'redis', 'document database'],
    'postgresql':              ['postgres', 'psql', 'sql'],
    'postgres':                ['postgresql', 'sql'],
    'mysql':                   ['mariadb', 'sql'],
    'mariadb':                 ['mysql', 'sql'],
    'sql server':              ['microsoft sql server', 'mssql', 't-sql', 'tsql'],
    'microsoft sql server':    ['sql server', 'mssql', 't-sql'],
    'mssql':                   ['sql server', 'microsoft sql server', 't-sql'],
    'oracle':                  ['oracle db', 'oracle database', 'pl/sql', 'plsql', 'oracle ebs', 'oracle fusion'],
    'oracle db':               ['oracle', 'oracle database'],
    'oracle database':         ['oracle', 'oracle db'],
    'oracle ebs':              ['oracle e-business suite', 'ebs', 'oracle'],
    'oracle fusion':           ['oracle fusion cloud', 'oracle erp cloud', 'oracle cloud'],
    'mongodb':                 ['mongo', 'nosql', 'document database'],
    'mongo':                   ['mongodb'],
    'redis':                   ['cache', 'in-memory database', 'key-value store'],
    'dynamodb':                ['nosql', 'aws', 'key-value store'],
    'cassandra':               ['nosql', 'wide-column store'],
    'elasticsearch':           ['elastic', 'opensearch', 'lucene', 'search engine'],
    'snowflake':               ['data warehouse', 'cloud data warehouse'],
    'bigquery':                ['gcp', 'data warehouse', 'google cloud'],
    'redshift':                ['aws', 'data warehouse'],
    'stored procedures':       ['sp', 'stored procs', 'sql', 'pl/sql', 't-sql'],
    'data modeling':           ['data model', 'erd', 'schema design', 'database design'],
    'database design':         ['data modeling', 'schema design', 'erd'],
    'query optimization':      ['sql tuning', 'performance tuning', 'indexing'],

    # ========================================================================
    # CLOUD
    # ========================================================================
    'aws':                     ['amazon web services', 'amazon aws', 'aws cloud'],
    'amazon web services':     ['aws'],
    'azure':                   ['microsoft azure', 'azure cloud'],
    'microsoft azure':         ['azure'],
    'gcp':                     ['google cloud', 'google cloud platform'],
    'google cloud':            ['gcp', 'google cloud platform'],
    'google cloud platform':   ['gcp', 'google cloud'],
    'oracle cloud':            ['oci', 'oracle cloud infrastructure'],
    'oci':                     ['oracle cloud', 'oracle cloud infrastructure'],
    'cloud':                   ['aws', 'azure', 'gcp', 'oracle cloud', 'cloud computing', 'cloud platform'],
    'cloud infrastructure':    ['aws', 'azure', 'gcp', 'oracle cloud', 'iaas', 'paas', 'infrastructure as a service'],
    'cloud computing':         ['aws', 'azure', 'gcp', 'cloud'],
    'cloud platforms':         ['aws', 'azure', 'gcp', 'cloud platform'],
    'iaas':                    ['infrastructure as a service', 'cloud infrastructure'],
    'paas':                    ['platform as a service'],
    'saas':                    ['software as a service'],
    'serverless':              ['lambda', 'aws lambda', 'azure functions', 'cloud functions', 'faas'],

    # AWS services
    'lambda':                  ['aws lambda', 'serverless', 'faas'],
    'aws lambda':              ['lambda', 'serverless'],
    's3':                      ['aws s3', 'object storage', 'simple storage service'],
    'ec2':                     ['aws ec2', 'elastic compute cloud', 'aws compute'],
    'rds':                     ['aws rds', 'amazon rds', 'managed database'],
    'dynamodb':                ['aws dynamodb', 'nosql', 'key-value store'],
    'cloudwatch':              ['aws cloudwatch', 'monitoring', 'aws monitoring'],
    'cloudfront':              ['aws cloudfront', 'cdn'],
    'route53':                 ['aws route 53', 'route 53', 'dns'],
    'route 53':                ['route53', 'aws route53', 'dns'],
    'iam':                     ['aws iam', 'identity and access management', 'identity management'],
    'sns':                     ['aws sns', 'simple notification service', 'pub/sub'],
    'sqs':                     ['aws sqs', 'simple queue service', 'message queue'],
    'eks':                     ['aws eks', 'elastic kubernetes service', 'kubernetes'],
    'ecs':                     ['aws ecs', 'elastic container service'],
    'sagemaker':               ['aws sagemaker', 'ml', 'machine learning'],
    'api gateway':             ['aws api gateway', 'api management'],

    # Azure services
    'azure ad':                ['azure active directory', 'entra id', 'aad'],
    'azure active directory':  ['azure ad', 'entra id', 'aad'],
    'entra id':                ['azure ad', 'azure active directory'],
    'azure functions':         ['azure', 'serverless', 'faas'],
    'aks':                     ['azure kubernetes service', 'kubernetes'],
    'azure devops':            ['ado', 'tfs', 'vsts', 'azure pipelines'],

    # GCP services
    'gke':                     ['google kubernetes engine', 'kubernetes'],
    'gce':                     ['google compute engine'],
    'vertex ai':                ['gcp', 'machine learning', 'ml'],

    # ========================================================================
    # CONTAINERS / ORCHESTRATION
    # ========================================================================
    'docker':                  ['containers', 'containerization', 'docker compose'],
    'kubernetes':              ['k8s', 'eks', 'gke', 'aks', 'orchestration', 'container orchestration'],
    'k8s':                     ['kubernetes'],
    'helm':                    ['kubernetes', 'k8s'],
    'openshift':               ['kubernetes', 'red hat'],
    'containers':              ['docker', 'containerization'],
    'containerization':        ['docker', 'kubernetes', 'containers'],

    # ========================================================================
    # CI/CD / DEVOPS
    # ========================================================================
    'ci/cd':                   ['cicd', 'ci cd', 'continuous integration', 'continuous deployment', 'continuous delivery', 'jenkins', 'github actions', 'gitlab ci', 'pipelines'],
    'cicd':                    ['ci/cd', 'continuous integration', 'continuous deployment'],
    'continuous integration':  ['ci', 'ci/cd', 'cicd'],
    'continuous deployment':   ['cd', 'ci/cd', 'cicd', 'continuous delivery'],
    'continuous delivery':     ['ci/cd', 'cicd', 'continuous deployment'],
    'jenkins':                 ['ci/cd pipeline', 'jenkinsfile'],
    'github actions':          ['ci/cd', 'github workflows'],
    'gitlab ci':               ['ci/cd', 'gitlab pipelines'],
    'circleci':                ['ci/cd'],
    'argocd':                  ['gitops', 'kubernetes', 'continuous deployment'],
    'devops':                  ['ci/cd', 'sre', 'infrastructure as code', 'gitops'],
    'sre':                     ['site reliability engineering', 'devops', 'reliability'],
    'site reliability engineering': ['sre', 'devops'],
    'gitops':                  ['argocd', 'flux', 'devops'],
    'infrastructure as code':  ['iac', 'terraform', 'cloudformation', 'pulumi', 'ansible'],
    'iac':                     ['infrastructure as code', 'terraform', 'cloudformation'],
    'terraform':               ['iac', 'infrastructure as code', 'hashicorp'],
    'ansible':                 ['configuration management', 'iac'],
    'puppet':                  ['configuration management', 'iac'],
    'chef':                    ['configuration management', 'iac'],

    # ========================================================================
    # OBSERVABILITY / MONITORING
    # ========================================================================
    'monitoring':              ['observability', 'cloudwatch', 'datadog', 'new relic', 'splunk', 'prometheus', 'grafana'],
    'observability':           ['monitoring', 'logging', 'tracing', 'metrics', 'apm'],
    'logging':                 ['log aggregation', 'splunk', 'elk', 'logstash', 'fluentd', 'cloudwatch logs'],
    'tracing':                 ['distributed tracing', 'jaeger', 'zipkin', 'opentelemetry'],
    'metrics':                 ['prometheus', 'grafana', 'cloudwatch', 'observability'],
    'apm':                     ['application performance monitoring', 'datadog', 'new relic', 'observability'],
    'splunk':                  ['log aggregation', 'siem', 'logging'],
    'datadog':                 ['monitoring', 'apm', 'observability'],
    'new relic':                ['monitoring', 'apm', 'observability'],
    'prometheus':              ['monitoring', 'metrics', 'grafana'],
    'grafana':                 ['monitoring', 'dashboards', 'prometheus'],
    'elk':                     ['elasticsearch', 'logstash', 'kibana', 'logging'],
    'kibana':                  ['elk', 'elasticsearch', 'logging'],
    'opentelemetry':           ['otel', 'observability', 'tracing'],

    # ========================================================================
    # IDES / EDITORS
    # ========================================================================
    'ide':                     ['vs code', 'vscode', 'visual studio', 'intellij', 'pycharm', 'eclipse', 'webstorm', 'rider', 'goland', 'android studio', 'xcode'],
    'vs code':                 ['vscode', 'visual studio code', 'ide'],
    'vscode':                  ['vs code', 'visual studio code', 'ide'],
    'visual studio':           ['vs', 'visual studio code', 'ide'],
    'intellij':                ['intellij idea', 'jetbrains', 'ide'],
    'pycharm':                 ['jetbrains', 'ide', 'python ide'],
    'eclipse':                 ['ide', 'java ide'],
    'xcode':                   ['ide', 'ios', 'mac'],
    'android studio':          ['ide', 'android'],

    # ========================================================================
    # OPERATING SYSTEMS
    # ========================================================================
    'linux':                   ['ubuntu', 'debian', 'centos', 'rhel', 'red hat', 'fedora', 'unix', 'gnu/linux'],
    'unix':                    ['linux', 'solaris', 'aix', 'bsd', 'macos'],
    'ubuntu':                  ['linux', 'debian'],
    'rhel':                    ['red hat', 'red hat enterprise linux', 'linux'],
    'red hat':                 ['rhel', 'linux'],
    'macos':                   ['mac os', 'mac', 'osx', 'os x'],
    'windows':                 ['windows server', 'windows 10', 'windows 11', 'microsoft windows'],
    'wsl':                     ['windows subsystem for linux'],
    'windows subsystem for linux': ['wsl'],

    # ========================================================================
    # METHODOLOGY / PROCESS
    # ========================================================================
    'agile':                   ['scrum', 'kanban', 'sprint', 'sprints', 'iterative', 'agile methodology', 'safe'],
    'scrum':                   ['agile', 'sprint', 'sprints', 'scrum master', 'product owner'],
    'kanban':                  ['agile', 'lean', 'kanban board'],
    'sprint':                  ['agile', 'scrum', 'sprints', 'iteration'],
    'sprints':                 ['sprint', 'agile', 'scrum'],
    'waterfall':               ['traditional sdlc', 'sequential development'],
    'sdlc':                    ['software development life cycle', 'software development lifecycle', 'development life cycle'],
    'software development life cycle': ['sdlc', 'software development lifecycle'],
    'development life cycle':  ['sdlc', 'software development life cycle'],
    'devops':                  ['ci/cd', 'sre', 'infrastructure as code'],
    'lean':                    ['agile', 'lean six sigma', 'kanban'],
    'six sigma':               ['lean six sigma', 'process improvement'],
    'itil':                    ['itil 4', 'itil4', 'itsm', 'itil foundations'],
    'itil 4':                  ['itil', 'itil4', 'itsm'],
    'itil4':                   ['itil', 'itil 4', 'itsm'],
    'itsm':                    ['itil', 'service management', 'it service management'],
    'project management':      ['pmp', 'capm', 'pmbok', 'prince2', 'program management'],
    'business analysis':       ['business analyst', 'ba', 'requirements gathering'],
    'business analyst':        ['business analysis', 'ba', 'requirements'],
    'change management':       ['itil', 'release management', 'deployment process'],
    'risk management':         ['risk assessment', 'compliance', 'governance', 'risk mitigation'],

    # ========================================================================
    # TESTING / QA
    # ========================================================================
    'unit test':               ['unit testing', 'unit tests', 'testing', 'pytest', 'junit', 'jest', 'mocha', 'rspec', 'testng'],
    'unit tests':              ['unit test', 'unit testing'],
    'unit testing':            ['unit test', 'unit tests', 'testing'],
    'integration test':        ['integration testing', 'integration tests', 'testing', 'selenium'],
    'integration testing':     ['integration test', 'integration tests'],
    'integration tests':       ['integration test', 'integration testing'],
    'end-to-end testing':      ['e2e', 'e2e testing', 'cypress', 'playwright', 'selenium'],
    'e2e':                     ['end-to-end', 'end-to-end testing', 'e2e testing'],
    'e2e testing':             ['end-to-end testing', 'e2e'],
    'acceptance testing':      ['uat', 'user acceptance testing', 'acceptance criteria'],
    'uat':                     ['user acceptance testing', 'acceptance testing'],
    'acceptance criteria':     ['user stories', 'definition of done', 'agile', 'requirements'],
    'regression testing':      ['regression', 'test automation'],
    'performance testing':     ['load testing', 'stress testing', 'jmeter', 'gatling', 'k6'],
    'load testing':            ['performance testing', 'stress testing', 'jmeter'],
    'tdd':                     ['test-driven development', 'test driven development', 'unit testing'],
    'bdd':                     ['behavior-driven development', 'cucumber', 'gherkin'],
    'qa':                      ['quality assurance', 'testing', 'quality engineering'],
    'quality assurance':       ['qa', 'testing'],
    'test automation':         ['automated testing', 'selenium', 'cypress', 'playwright'],
    'selenium':                ['webdriver', 'test automation', 'browser automation'],
    'cypress':                 ['e2e testing', 'test automation', 'browser automation'],
    'playwright':              ['e2e testing', 'test automation', 'browser automation'],
    'jest':                    ['unit testing', 'javascript testing'],
    'pytest':                  ['unit testing', 'python testing'],
    'junit':                   ['unit testing', 'java testing'],

    # ========================================================================
    # ARCHITECTURE / DESIGN
    # ========================================================================
    'microservices':           ['microservice', 'service-oriented', 'distributed systems', 'service mesh'],
    'microservice':            ['microservices'],
    'monolith':                ['monolithic', 'monolithic architecture'],
    'monolithic':              ['monolith'],
    'soa':                     ['service-oriented architecture', 'services'],
    'service-oriented architecture': ['soa'],
    'event-driven':            ['event-driven architecture', 'event sourcing', 'kafka', 'pub/sub'],
    'event-driven architecture': ['event-driven', 'eda'],
    'design patterns':         ['gof patterns', 'oop patterns', 'singleton', 'factory', 'observer', 'mvc', 'mvvm'],
    'distributed systems':     ['microservices', 'distributed computing', 'consensus'],
    'system design':           ['architecture', 'distributed systems', 'scalability'],
    'oop':                     ['object-oriented programming', 'object oriented'],
    'object-oriented programming': ['oop', 'object oriented'],
    'functional programming':  ['fp', 'lambda calculus', 'haskell', 'scala', 'erlang'],
    'mvc':                     ['model-view-controller', 'design pattern'],
    'rest architecture':       ['restful', 'rest', 'api design'],
    'clean code':              ['clean architecture', 'solid', 'best practices'],
    'solid':                   ['solid principles', 'oop', 'clean code'],
    'ddd':                     ['domain-driven design'],
    'cqrs':                    ['command query responsibility segregation', 'event sourcing'],

    # ========================================================================
    # SECURITY
    # ========================================================================
    'cybersecurity':           ['cyber security', 'information security', 'infosec', 'security'],
    'cyber security':          ['cybersecurity', 'information security'],
    'information security':    ['infosec', 'cybersecurity'],
    'infosec':                 ['information security', 'cybersecurity'],
    'security':                ['cybersecurity', 'information security', 'security audit', 'security awareness'],
    'security audit':          ['vulnerability assessment', 'penetration testing', 'compliance', 'audit'],
    'vulnerability':           ['vulnerability assessment', 'vulnerability management', 'cve'],
    'vulnerability assessment': ['vulnerability', 'vulnerability scanning', 'pen testing'],
    'penetration testing':     ['pen test', 'pentest', 'pentesting', 'ethical hacking'],
    'pen testing':             ['penetration testing', 'pentest'],
    'pentest':                 ['penetration testing', 'pen test'],
    'ethical hacking':         ['penetration testing', 'red team'],
    'rbac':                    ['role-based access control', 'access control', 'iam'],
    'role-based access control': ['rbac', 'access control'],
    'access control':          ['rbac', 'iam', 'access management', 'permissions'],
    'iam':                     ['identity and access management', 'identity management', 'access management'],
    'identity and access management': ['iam', 'identity management'],
    'sso':                     ['single sign-on', 'single sign on', 'saml', 'oauth', 'okta'],
    'single sign-on':          ['sso', 'saml', 'oauth'],
    'mfa':                     ['multi-factor authentication', '2fa', 'two-factor authentication'],
    'multi-factor authentication': ['mfa', '2fa'],
    '2fa':                     ['multi-factor authentication', 'mfa'],
    'oauth':                   ['oauth2', 'authorization', 'sso'],
    'oauth2':                  ['oauth', 'authorization'],
    'jwt':                     ['json web token', 'authentication', 'tokens'],
    'saml':                    ['sso', 'authentication'],
    'encryption':              ['cryptography', 'tls', 'ssl', 'aes', 'rsa'],
    'cryptography':            ['encryption', 'crypto', 'hashing'],
    'tls':                     ['ssl', 'https', 'encryption'],
    'ssl':                     ['tls', 'https', 'encryption'],
    'firewall':                ['network security', 'security', 'waf'],
    'siem':                    ['splunk', 'security monitoring', 'log analysis'],
    'compliance':              ['governance', 'audit', 'soc 2', 'iso 27001', 'gdpr', 'hipaa'],
    'soc 2':                   ['soc2', 'compliance', 'audit'],
    'soc2':                    ['soc 2', 'compliance'],
    'iso 27001':               ['compliance', 'security standard'],
    'gdpr':                    ['data privacy', 'compliance', 'privacy'],
    'hipaa':                   ['compliance', 'healthcare privacy'],
    'pci dss':                 ['compliance', 'payment security'],
    'owasp':                   ['owasp top 10', 'web security', 'application security'],

    # ========================================================================
    # SERVICE DESK / IT SUPPORT
    # ========================================================================
    'service desk':            ['help desk', 'helpdesk', 'technical support', 'tier 1', 'tier 2', 'l1', 'l2'],
    'help desk':               ['service desk', 'helpdesk', 'technical support'],
    'helpdesk':                ['help desk', 'service desk'],
    'technical support':       ['service desk', 'help desk', 'desktop support', 'troubleshooting'],
    'desktop support':         ['technical support', 'service desk'],
    'troubleshooting':         ['technical support', 'debugging', 'problem solving', 'root cause analysis'],
    'incident management':     ['incident response', 'itil', 'ticketing'],
    'incident response':       ['incident management', 'security incident'],
    'problem management':      ['root cause analysis', 'itil'],
    'ticketing':               ['ticketing system', 'service desk', 'jira', 'servicenow', 'zendesk'],
    'sop':                     ['standard operating procedure', 'sops', 'runbook', 'documentation'],
    'sops':                    ['sop', 'standard operating procedures'],
    'standard operating procedure': ['sop', 'sops', 'runbook'],
    'runbook':                 ['runbooks', 'sop', 'playbook', 'documentation'],
    'runbooks':                ['runbook', 'sop'],
    'knowledge base':          ['kb', 'documentation', 'kb articles', 'wiki'],
    'asset management':        ['lifecycle management', 'inventory management'],
    'lifecycle management':    ['asset management', 'asset lifecycle'],

    # ========================================================================
    # ACTIVE DIRECTORY / IT INFRA
    # ========================================================================
    'active directory':        ['ad', 'azure ad', 'azure active directory', 'ldap'],
    'ad':                      ['active directory', 'azure ad'],
    'group policy':            ['gpo', 'group policies', 'windows policies'],
    'group policies':          ['group policy', 'gpo'],
    'gpo':                     ['group policy', 'group policies'],
    'intune':                  ['microsoft intune', 'mdm', 'device management'],
    'microsoft intune':        ['intune', 'mdm'],
    'mdm':                     ['mobile device management', 'intune', 'jamf'],
    'sccm':                    ['system center configuration manager', 'mecm'],
    'office 365':              ['microsoft 365', 'm365', 'o365'],
    'microsoft 365':           ['office 365', 'm365', 'o365'],
    'm365':                    ['microsoft 365', 'office 365'],
    'sharepoint':              ['microsoft sharepoint', 'collaboration platform'],
    'exchange':                ['microsoft exchange', 'email server'],
    'vmware':                  ['esxi', 'vsphere', 'virtualization'],
    'virtualization':          ['vmware', 'hyper-v', 'kvm', 'hypervisor'],
    'hyper-v':                 ['virtualization', 'microsoft hyper-v'],
    'backup':                  ['backup and recovery', 'disaster recovery', 'data protection'],
    'disaster recovery':       ['dr', 'business continuity', 'failover', 'backup'],
    'high availability':       ['ha', 'failover', 'redundancy', 'clustering'],

    # ========================================================================
    # ENTERPRISE / ERP
    # ========================================================================
    'sap':                     ['sap hana', 'sap erp', 's/4hana'],
    'oracle erp':              ['oracle fusion', 'oracle ebs', 'erp'],
    'workday':                 ['hcm', 'human capital management'],
    'salesforce':              ['sfdc', 'apex', 'lightning', 'crm'],
    'sfdc':                    ['salesforce'],
    'servicenow':              ['itsm', 'ticketing', 'service desk platform'],
    'jira':                    ['atlassian', 'agile', 'ticketing'],
    'confluence':              ['atlassian', 'wiki', 'documentation'],
    'powerbi':                 ['power bi', 'business intelligence', 'bi', 'reporting'],
    'power bi':                ['powerbi', 'business intelligence', 'bi'],
    'tableau':                 ['business intelligence', 'bi', 'data visualization'],
    'looker':                  ['business intelligence', 'bi'],
    'business intelligence':   ['bi', 'powerbi', 'tableau', 'looker', 'reporting'],
    'bi':                      ['business intelligence', 'powerbi', 'tableau'],

    # ========================================================================
    # DATA / ML / AI
    # ========================================================================
    'machine learning':        ['ml', 'ai', 'deep learning', 'neural networks', 'tensorflow', 'pytorch', 'scikit-learn'],
    'ml':                      ['machine learning', 'ai'],
    'ai':                      ['artificial intelligence', 'machine learning', 'ml'],
    'artificial intelligence': ['ai', 'machine learning', 'ml'],
    'deep learning':           ['neural networks', 'tensorflow', 'pytorch', 'machine learning'],
    'neural networks':         ['deep learning', 'cnn', 'rnn', 'transformers'],
    'nlp':                     ['natural language processing', 'transformers', 'llm'],
    'natural language processing': ['nlp', 'transformers', 'language models'],
    'computer vision':         ['cv', 'image processing', 'cnn', 'opencv'],
    'llm':                     ['large language models', 'gpt', 'transformer'],
    'large language models':   ['llm', 'gpt', 'transformer'],
    'rag':                     ['retrieval augmented generation', 'vector search', 'embeddings'],
    'tensorflow':              ['tf', 'keras', 'deep learning'],
    'pytorch':                 ['torch', 'deep learning'],
    'scikit-learn':            ['sklearn', 'machine learning'],
    'sklearn':                 ['scikit-learn'],
    'pandas':                  ['data analysis', 'python', 'dataframes'],
    'numpy':                   ['numerical computing', 'python', 'arrays'],
    'data science':            ['data analysis', 'machine learning', 'statistics'],
    'data analysis':           ['data science', 'analytics', 'pandas', 'sql'],
    'data engineering':        ['etl', 'data pipeline', 'spark', 'airflow'],
    'etl':                     ['extract transform load', 'elt', 'data pipeline', 'data integration'],
    'elt':                     ['etl', 'extract load transform', 'data pipeline'],
    'data pipeline':           ['etl', 'elt', 'airflow', 'data engineering'],
    'data warehouse':          ['snowflake', 'redshift', 'bigquery', 'data warehousing'],
    'data warehousing':        ['data warehouse', 'snowflake', 'redshift'],
    'data lake':               ['s3', 'data lakehouse', 'big data'],
    'big data':                ['hadoop', 'spark', 'data lake', 'distributed computing'],
    'spark':                   ['apache spark', 'pyspark', 'big data'],
    'apache spark':            ['spark', 'pyspark'],
    'pyspark':                 ['spark', 'apache spark', 'python'],
    'hadoop':                  ['hdfs', 'mapreduce', 'big data'],
    'kafka':                   ['apache kafka', 'event streaming', 'message broker'],
    'apache kafka':            ['kafka', 'event streaming'],
    'airflow':                 ['apache airflow', 'data pipeline', 'workflow orchestration'],
    'data migration':          ['data conversion', 'etl', 'database migration'],
    'data conversion':         ['data migration', 'etl'],

    # ========================================================================
    # MOBILE
    # ========================================================================
    'ios':                     ['iphone', 'ipad', 'swift', 'objective-c', 'xcode'],
    'android':                 ['kotlin', 'java', 'android studio'],
    'react native':            ['mobile', 'cross-platform', 'react'],
    'flutter':                 ['dart', 'mobile', 'cross-platform'],
    'mobile development':      ['ios', 'android', 'react native', 'flutter', 'mobile apps'],

    # ========================================================================
    # NETWORKING
    # ========================================================================
    'tcp/ip':                  ['networking', 'tcp', 'ip'],
    'dns':                     ['domain name system', 'networking', 'route 53'],
    'load balancing':          ['load balancer', 'haproxy', 'nginx', 'elb'],
    'load balancer':           ['load balancing'],
    'cdn':                     ['content delivery network', 'cloudfront', 'cloudflare'],
    'vpn':                     ['virtual private network', 'remote access'],
    'firewall':                ['network security', 'waf', 'security groups'],
    'networking':              ['tcp/ip', 'dns', 'routing', 'switching'],

    # ========================================================================
    # SOFT / GENERAL
    # ========================================================================
    'communication':           ['written communication', 'verbal communication', 'presentation'],
    'leadership':              ['team lead', 'mentoring', 'management', 'led'],
    'teamwork':                ['collaboration', 'team-oriented', 'cross-functional'],
    'collaboration':           ['teamwork', 'cross-functional'],
    'cross-functional':        ['cross functional', 'collaboration', 'teamwork'],
    'cross functional':        ['cross-functional'],
    'problem solving':         ['problem-solving', 'troubleshooting', 'analytical', 'critical thinking'],
    'problem-solving':         ['problem solving'],
    'critical thinking':       ['analytical', 'problem solving'],
    'analytical':              ['analysis', 'critical thinking', 'data analysis'],
    'mentoring':               ['coaching', 'training', 'leadership'],
    'documentation':           ['technical writing', 'sop', 'runbook', 'knowledge base'],
    'technical writing':       ['documentation', 'sops', 'runbooks'],
    'stakeholder':             ['stakeholders', 'stakeholder management'],
    'stakeholders':            ['stakeholder', 'stakeholder management'],
    'requirements gathering':  ['requirements analysis', 'business analysis', 'use cases'],
    'requirements analysis':   ['requirements gathering', 'business analysis'],
    'use cases':               ['user stories', 'requirements'],
    'user stories':            ['use cases', 'agile', 'requirements'],

    # ========================================================================
    # KEYWORDS WITH NO USEFUL NEAR-MISS (you have it or you don't)
    # ========================================================================
    'jenkins':                 [],
    'splunk':                  [],
    'kafka':                   ['apache kafka', 'event streaming'],
    'snowflake':               ['data warehouse'],
    'tableau':                 ['business intelligence', 'bi'],
    'salesforce':              ['sfdc', 'crm'],
    'sap':                     ['enterprise software', 'erp'],
    'workday':                 ['hcm', 'human capital management'],
    'servicenow':              ['itsm', 'ticketing'],
    'okta':                    ['sso', 'iam'],
    'auth0':                   ['sso', 'iam', 'authentication'],
    'stripe':                  ['payments', 'payment processing'],
    'twilio':                  ['sms', 'communications api'],

    # ========================================================================
    # CERTIFICATIONS
    # ========================================================================
    'aws certified':           ['aws certification', 'aws solutions architect'],
    'azure certified':         ['azure certification', 'az-104', 'az-900'],
    'pmp':                     ['project management professional', 'project management'],
    'cissp':                   ['security certification', 'cybersecurity'],
    'security+':               ['comptia security+', 'security certification'],
    'ccna':                    ['cisco certification', 'networking'],
    'cspo':                    ['certified scrum product owner', 'product owner'],
    'csm':                     ['certified scrum master', 'scrum master'],
}
def find_near_misses(missing_keywords, resume_text):
    """For each missing keyword, check if the resume has a related term."""
    resume_lower = resume_text.lower()
    near_misses = {}

    for kw in missing_keywords:
        hints = NEAR_MISS_HINTS.get(kw, [])
        found_hints = []
        for hint in hints:
            # Use the same strict matching
            if '/' in hint or '.' in hint:
                pattern = rf'(?<!\w){re.escape(hint)}(?!\w)'
            else:
                pattern = rf'\b{re.escape(hint)}\b'
            if re.search(pattern, resume_lower):
                found_hints.append(hint)
        if found_hints:
            near_misses[kw] = found_hints

    return near_misses




# ===== 5. MATCHING =====

def match_resume_to_jd(resume_text, jd_text):
    """Strict ATS-style matching: word-boundary regex, no variants."""
    resume_normalized = re.sub(r'\s+', ' ', resume_text.lower())
    jd_keywords = extract_jd_keywords(jd_text)
    must_haves = find_must_haves(jd_text, jd_keywords)

    def keyword_present(keyword, text):
        # Escape regex special chars; allow / and . to match literally
        escaped = re.escape(keyword)
        # Word boundary on both sides — but \b doesn't work well with /
        # so for keywords containing /, use lookarounds
        if '/' in keyword or '.' in keyword or '+' in keyword or '#' in keyword:
            pattern = rf'(?<!\w){escaped}(?!\w)'
        else:
            pattern = rf'\b{escaped}\b'
        return bool(re.search(pattern, text))

    matched = {kw for kw in jd_keywords if keyword_present(kw, resume_normalized)}
    missing = jd_keywords - matched
    missing_critical = must_haves - matched

    return {
        'jd_keywords': jd_keywords,
        'matched': matched,
        'missing': missing,
        'must_haves': must_haves,
        'missing_critical': missing_critical,
        'match_rate': len(matched) / len(jd_keywords) if jd_keywords else 0,
        'critical_match_rate': (
            len(must_haves & matched) / len(must_haves) if must_haves else 1.0
        ),
    }

# ===== 6. TOKENIZATION RISK CHECKS =====

def check_tokenization_risks(resume_text, jd_text):
    """Flag specific failure modes the Reddit post warned about."""
    warnings = []

    # Compound word splits
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    compound_pairs = [
        ('cross-functional', 'crossfunctional'),
        ('role-based', 'rolebased'),
        ('real-time', 'realtime'),
        ('full-stack', 'fullstack'),
        ('back-end', 'backend'),
        ('front-end', 'frontend'),
    ]
    for hyphenated, joined in compound_pairs:
        in_jd = hyphenated in jd_lower or joined in jd_lower
        in_resume = hyphenated in resume_lower or joined in resume_lower
        if in_jd and not in_resume:
            warnings.append(f"JD uses '{hyphenated}' — not found in resume")

    # Acronym vs spelled-out
    acronym_pairs = [
        ('rbac', 'role-based access control'),
        ('ad', 'active directory'),
        ('dba', 'database administrator'),
        ('ci/cd', 'continuous integration'),
        ('sop', 'standard operating procedure'),
    ]
    for acronym, full in acronym_pairs:
        jd_has_acronym = re.search(rf'\b{re.escape(acronym)}\b', jd_lower)
        jd_has_full = full in jd_lower
        resume_has_acronym = re.search(rf'\b{re.escape(acronym)}\b', resume_lower)
        resume_has_full = full in resume_lower
        if (jd_has_acronym or jd_has_full) and not (resume_has_acronym and resume_has_full):
            if jd_has_acronym and not resume_has_acronym:
                warnings.append(f"JD uses acronym '{acronym.upper()}' — add it alongside '{full}' in resume")
            if jd_has_full and not resume_has_full:
                warnings.append(f"JD uses full phrase '{full}' — spell it out in resume")

    return warnings


# ===== 7. REPORT =====

def print_report(result, risk_warnings, near_misses):
    print("=" * 70)
    print("ATS MATCH REPORT (strict word-boundary mode)")
    print("=" * 70)

    rate = result['match_rate'] * 100
    crit = result['critical_match_rate'] * 100

    print(f"\n📊 Overall keyword match: {len(result['matched'])}/{len(result['jd_keywords'])} ({rate:.0f}%)")
    print(f"🎯 Must-have match:       {len(result['must_haves'] & result['matched'])}/{len(result['must_haves'])} ({crit:.0f}%)")

    print("\n" + "─" * 70)
    if rate >= 75:
        print("✅ STRONG MATCH — likely to pass keyword screening")
    elif rate >= 50:
        print("🟡 MODERATE MATCH — borderline, optimize gaps below")
    else:
        print("🔴 WEAK MATCH — significant gaps, likely auto-rejected")
    print("─" * 70)

    print(f"\n✅ MATCHED KEYWORDS ({len(result['matched'])}):")
    for kw in sorted(result['matched']):
        print(f"   ✓ {kw}")

    print(f"\n❌ MISSING KEYWORDS ({len(result['missing'])}):")
    for kw in sorted(result['missing']):
        marker = "🔴" if kw in result['missing_critical'] else "  "
        hint_note = ""
        if kw in near_misses:
            hint_note = f"  ← you have: {', '.join(near_misses[kw])}"
        print(f"   {marker} {kw}{hint_note}")

    if result['missing_critical']:
        print(f"\n⚠️  CRITICAL GAPS (mentioned as required in JD):")
        for kw in sorted(result['missing_critical']):
            print(f"   🔴 {kw}")

    if near_misses:
        print(f"\n💡 NEAR-MISSES (easy wins — add the exact phrase):")
        for kw, hints in sorted(near_misses.items()):
            print(f"   • JD wants '{kw}' — you wrote '{hints[0]}'. Add '{kw}' explicitly.")

    if risk_warnings:
        print(f"\n⚠️  TOKENIZATION RISKS:")
        for w in risk_warnings:
            print(f"   • {w}")

    print("\n" + "=" * 70)

# ===== 8. RUN =====

if __name__ == '__main__':
    resume_text = extract_resume_text(RESUME_PATH)
    if not JOB_DESCRIPTION.strip() or 'PASTE THE FULL' in JOB_DESCRIPTION:
        print("❌ Please paste a job description into the JOB_DESCRIPTION variable.")
        exit(1)

    result = match_resume_to_jd(resume_text, JOB_DESCRIPTION)
    risks = check_tokenization_risks(resume_text, JOB_DESCRIPTION)
    near_misses = find_near_misses(result['missing'], resume_text)
    print_report(result, risks, near_misses)