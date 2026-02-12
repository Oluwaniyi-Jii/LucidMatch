import { useState, useEffect, useRef } from 'react';
import {
    Box,
    Container,
    Heading,
    Text,
    VStack,
    HStack,
    Button,
    Textarea,
    Select,
    Card,
    CardHeader,
    CardBody,
    SimpleGrid,
    Badge,
    Progress,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Alert,
    AlertIcon,
    AlertTitle,
    AlertDescription,
    Divider,
    Accordion,
    AccordionItem,
    AccordionButton,
    AccordionPanel,
    AccordionIcon,
    Tag,
    TagLabel,
    Wrap,
    WrapItem,
    Switch,
    FormControl,
    FormLabel,
    useToast,
    Icon,
    Flex,
    Spacer,
    CircularProgress,
    CircularProgressLabel,
    Input,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    TableContainer,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalFooter,
    ModalCloseButton,
    useDisclosure,
    Spinner,
    IconButton,
    Tooltip,
} from '@chakra-ui/react';
import {
    FiAlertTriangle,
    FiShield,
    FiBook,
    FiUser,
    FiTarget,
    FiAward,
    FiClock,
    FiCheckCircle,
    FiUploadCloud,
    FiDollarSign,
    FiDownload,
    FiAlertOctagon,
    FiArrowRight,
    FiZap,
    FiInfo,
    FiPlay,
    FiGlobe,
    FiStar,
    FiHelpCircle,
    FiRefreshCw,
} from 'react-icons/fi';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip as ChartTooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Radar, Bar } from 'react-chartjs-2';
import { getHealthStatus, getJobs, fullAnalysis } from './api';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, ChartTooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement);

const COST_PER_PROFILE = 0.12;

const DEMO_PROFILES = [
    {
        id: 'pivot-nurse-to-ux',
        name: 'The Pivot',
        icon: FiRefreshCw,
        color: 'purple',
        description: 'Nurse to UX Research',
        resume: `PROFESSIONAL SUMMARY
Dedicated healthcare professional with 5 years of experience in acute care nursing. Seeking to transition skills to user experience research.

PROFESSIONAL EXPERIENCE
Registered Nurse, Cardiac Care Unit | Major Metropolitan Hospital | 2019 - Present
- Conduct comprehensive patient assessments and develop individualized care plans
- Lead family conferences to discuss treatment options and gather patient preferences
- Train and mentor 12 new nursing staff members on patient communication protocols
- Implemented new patient feedback system that improved satisfaction scores by 23%

Patient Experience Coordinator (Part-time) | 2021 - 2022
- Designed and administered patient satisfaction surveys (300+ responses)
- Analyzed survey data to identify improvement opportunities
- Facilitated focus groups with patients and families

EDUCATION
Bachelor of Science in Nursing | State University | 2019

SKILLS
Active Listening, Empathy, Qualitative Data Collection, Survey Design, Stakeholder Communication, Documentation`
    },
    {
        id: 'underdog-bootcamp',
        name: 'The Underdog',
        icon: FiStar,
        color: 'orange',
        description: 'Bootcamp Graduate',
        resume: `ABOUT ME
Self-taught developer who discovered programming through online courses while working retail. Completed intensive coding bootcamp and built production applications.

TECHNICAL PROJECTS
TaskFlow - Full-Stack Task Management App
- Built REST API with Python/FastAPI handling 1,000+ daily requests
- PostgreSQL database with optimized queries (reduced load time by 40%)
- React frontend with responsive design
- Deployed on AWS EC2 with Docker containers

WORK EXPERIENCE
Freelance Web Developer | 2023 - Present
- Delivered 5 client projects on time and within budget
- Built e-commerce site handling $50k+ monthly transactions

Retail Associate | 2018 - 2022
- Promoted twice for reliability and problem-solving

EDUCATION
Full-Stack Web Development Bootcamp | 2023 (16-week intensive)

TECHNICAL SKILLS
Python, JavaScript, SQL, React, FastAPI, PostgreSQL, MongoDB, Docker, AWS, Git`
    },
    {
        id: 'global-engineer',
        name: 'The Global',
        icon: FiGlobe,
        color: 'blue',
        description: 'International Engineer',
        resume: `PROFESSIONAL PROFILE
Experienced software engineer with 6 years of development experience across multiple countries. Fluent in English, Mandarin, and German.

PROFESSIONAL EXPERIENCE
Senior Software Development Engineer | Singapore | 2021 - Present
- Lead architect for real-time data processing pipeline serving 10M+ users
- Reduced system latency by 60% through optimization of Kafka consumers
- Mentored team of 5 junior developers

Software Engineer II | Shanghai | 2018 - 2021
- Developed recommendation engine using Python and Spark
- Built RESTful microservices handling 50K requests per second

Junior Developer | Berlin | 2017 - 2018
- Full-stack development with Python and React

EDUCATION
Master of Engineering, Computer Science | Germany | 2017
Bachelor of Engineering, Software Engineering | China | 2015

TECHNICAL SKILLS
Python, Java, Scala, Apache Spark, Kafka, PostgreSQL, AWS, Docker, Kubernetes`
    },
    {
        id: 'overqualified-phd',
        name: 'The Overqualified',
        icon: FiAward,
        color: 'green',
        description: 'PhD Applying Entry-Level',
        resume: `EDUCATION
Doctor of Philosophy in Physics | Research University | 2023
- Published 4 peer-reviewed papers in high-impact journals
- Presented at 6 international conferences

Bachelor of Science in Physics, summa cum laude | 2018

RESEARCH EXPERIENCE
Graduate Researcher | 2018 - 2023
- Developed novel machine learning models for physics simulations
- Analyzed datasets with millions of data points using Python and R
- Built statistical models achieving 95% prediction accuracy
- Automated data processing pipelines reducing analysis time by 80%

Data Science Intern | National Laboratory | Summer 2021
- Applied ML techniques to experimental physics data

TECHNICAL SKILLS
Python (NumPy, Pandas, Scikit-learn), R, SQL, Statistics, Machine Learning, Visualization

WHY DATA ANALYTICS
Seeking to apply quantitative skills in industry. Eager to learn industry practices.`
    },
    {
        id: 'sparse-profile',
        name: 'The Sparse',
        icon: FiHelpCircle,
        color: 'red',
        description: 'Minimal Resume (Safety Test)',
        resume: `John D.

Experience:
- Worked at tech company for 2 years
- Some programming experience
- Customer support background

Skills:
- Computers
- Microsoft Office
- Communication

Education:
- Associate degree

Looking for opportunities in tech industry.`
    }
];

function App() {
    const [resumeText, setResumeText] = useState('');
    const [fileName, setFileName] = useState('');
    const [selectedJob, setSelectedJob] = useState('');
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [apiStatus, setApiStatus] = useState(null);
    const [results, setResults] = useState(null);
    const [analysisCount, setAnalysisCount] = useState(0);
    const [selectedDemo, setSelectedDemo] = useState(null);
    const [demoMode, setDemoMode] = useState(false);
    const fileInputRef = useRef(null);
    const toast = useToast();
    const { isOpen: isTransferOpen, onOpen: onTransferOpen, onClose: onTransferClose } = useDisclosure();
    const { isOpen: isSummaryOpen, onOpen: onSummaryOpen, onClose: onSummaryClose } = useDisclosure();

    useEffect(() => {
        checkApiStatus();
        loadJobs();
    }, []);

    const checkApiStatus = async () => {
        try {
            const status = await getHealthStatus();
            setApiStatus(status);
        } catch (error) {
            setApiStatus({ status: 'error', message: 'Cannot connect to backend' });
        }
    };

    const loadJobs = async () => {
        try {
            const data = await getJobs();
            setJobs(data.jobs || []);
        } catch (error) {
            console.error('Failed to load jobs:', error);
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setFileName(file.name);
        setSelectedDemo(null);
        
        const reader = new FileReader();
        reader.onload = (e) => {
            setResumeText(e.target.result);
            toast({ title: 'File Uploaded', description: file.name, status: 'success', duration: 2000 });
        };
        reader.readAsText(file);
    };

    const selectDemoProfile = (profile) => {
        setSelectedDemo(profile.id);
        setResumeText(profile.resume);
        setFileName('');
        setResults(null);
        toast({ title: profile.name, description: profile.description, status: 'info', duration: 2000 });
    };

    const handleAnalyze = async () => {
        if (!resumeText.trim()) {
            toast({ title: 'No resume', description: 'Please upload or select a demo profile', status: 'warning', duration: 3000 });
            return;
        }

        setLoading(true);
        setResults(null);

        try {
            const jobIds = selectedJob ? [selectedJob] : null;
            const data = await fullAnalysis(resumeText, jobIds, true, true);
            setResults(data);
            setAnalysisCount(prev => prev + 1);
            toast({ title: 'Analysis Complete', description: `${data.total_processing_time_ms}ms`, status: 'success', duration: 3000 });
        } catch (error) {
            toast({ title: 'Analysis Failed', description: error.message, status: 'error', duration: 5000 });
        } finally {
            setLoading(false);
        }
    };

    const clearAll = () => {
        setResumeText('');
        setFileName('');
        setResults(null);
        setSelectedDemo(null);
    };

    const exportAuditLog = () => {
        if (!results?.audit?.decision_log) return;
        const content = `LUCIDMATCH AUDIT LOG\n${new Date().toISOString()}\n\n${results.audit.decision_log}`;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'audit_log.txt';
        a.click();
        URL.revokeObjectURL(url);
    };

    const isSafeMoment = () => {
        if (!results?.profile) return false;
        return results.profile.confidence_score < 0.5 || (results.top_match && results.top_match.overall_score < 30);
    };

    const getRadarData = (match) => {
        if (!match) return null;
        return {
            labels: ['Skills', 'Experience', 'Education', 'Achievements', 'Potential'],
            datasets: [
                { label: 'Candidate', data: [match.skills_match_score * 10, match.experience_match_score * 10, match.education_match_score * 10, match.achievement_match_score * 10, match.overall_score], backgroundColor: 'rgba(0, 115, 230, 0.2)', borderColor: 'rgba(0, 115, 230, 1)', borderWidth: 2 },
                { label: 'Requirement', data: [100, 100, 100, 100, 100], backgroundColor: 'rgba(200, 200, 200, 0.1)', borderColor: 'rgba(200, 200, 200, 0.5)', borderWidth: 1 },
            ],
        };
    };

    const getScoreDistribution = () => {
        if (!results?.matches) return null;
        return {
            labels: results.matches.map(m => m.job_title.split(' ').slice(0, 2).join(' ')),
            datasets: [{ label: 'Match %', data: results.matches.map(m => m.overall_score), backgroundColor: results.matches.map(m => m.overall_score >= 70 ? 'rgba(72, 187, 120, 0.7)' : m.overall_score >= 50 ? 'rgba(237, 137, 54, 0.7)' : 'rgba(245, 101, 101, 0.7)'), borderRadius: 8 }],
        };
    };

    const radarOptions = { scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } }, plugins: { legend: { position: 'bottom' } } };
    const barOptions = { indexAxis: 'y', scales: { x: { beginAtZero: true, max: 100 } }, plugins: { legend: { display: false } } };

    return (
        <Box minH="100vh" bg="gray.50">
            {/* Header */}
            <Box bg="white" borderBottom="1px" borderColor="gray.200" py={4} boxShadow="sm">
                <Container maxW="container.xl">
                    <Flex align="center">
                        <VStack align="start" spacing={0}>
                            <HStack>
                                <Heading size="lg" color="blue.600">LucidMatch</Heading>
                                {demoMode && <Badge colorScheme="purple" fontSize="sm">DEMO MODE</Badge>}
                            </HStack>
                            <Text fontSize="sm" color="gray.500">AI-Driven Talent Strategy Agent</Text>
                        </VStack>
                        <Spacer />
                        <HStack spacing={6}>
                            <FormControl display="flex" alignItems="center" w="auto">
                                <FormLabel mb={0} fontSize="sm" mr={2}>Demo Mode</FormLabel>
                                <Switch colorScheme="purple" isChecked={demoMode} onChange={(e) => setDemoMode(e.target.checked)} />
                            </FormControl>
                            <VStack spacing={0} align="end">
                                <HStack><Icon as={FiDollarSign} color="green.500" /><Text fontWeight="bold" color="green.600">${(analysisCount * COST_PER_PROFILE).toFixed(2)}</Text></HStack>
                                <Text fontSize="xs" color="gray.500">{analysisCount} profiles</Text>
                            </VStack>
                            <Divider orientation="vertical" h={10} />
                            <Badge colorScheme={apiStatus?.status === 'active' ? 'green' : 'red'} fontSize="sm">{apiStatus?.status || 'checking...'}</Badge>
                            {results && (
                                <Tooltip label="View Summary"><IconButton icon={<FiInfo />} onClick={onSummaryOpen} variant="ghost" colorScheme="blue" /></Tooltip>
                            )}
                        </HStack>
                    </Flex>
                </Container>
            </Box>

            <Container maxW="container.xl" py={6}>
                {/* Demo Mode Profiles */}
                {demoMode && (
                    <Card mb={6} bg="purple.50" borderColor="purple.200" borderWidth={2}>
                        <CardHeader pb={2}>
                            <HStack><Icon as={FiPlay} color="purple.500" /><Heading size="md" color="purple.700">Stress Test Scenarios</Heading></HStack>
                            <Text fontSize="sm" color="gray.600" mt={1}>Click a profile to load it for demo</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                            <SimpleGrid columns={{ base: 2, md: 5 }} spacing={3}>
                                {DEMO_PROFILES.map((profile) => (
                                    <Box
                                        key={profile.id}
                                        p={4}
                                        bg={selectedDemo === profile.id ? `${profile.color}.100` : 'white'}
                                        border="2px solid"
                                        borderColor={selectedDemo === profile.id ? `${profile.color}.400` : 'gray.200'}
                                        borderRadius="lg"
                                        cursor="pointer"
                                        onClick={() => selectDemoProfile(profile)}
                                        _hover={{ borderColor: `${profile.color}.400`, transform: 'translateY(-2px)', boxShadow: 'md' }}
                                        transition="all 0.2s"
                                    >
                                        <VStack spacing={2}>
                                            <Icon as={profile.icon} boxSize={8} color={`${profile.color}.500`} />
                                            <Text fontWeight="bold" fontSize="sm" textAlign="center">{profile.name}</Text>
                                            <Text fontSize="xs" color="gray.500" textAlign="center">{profile.description}</Text>
                                        </VStack>
                                    </Box>
                                ))}
                            </SimpleGrid>
                        </CardBody>
                    </Card>
                )}

                <Tabs variant="enclosed" colorScheme="blue">
                    <TabList>
                        <Tab><Icon as={FiUploadCloud} mr={2} /> Analyze</Tab>
                        <Tab><Icon as={FiTarget} mr={2} /> Results {results?.top_match && <Badge ml={2} colorScheme={results.top_match.overall_score >= 70 ? 'green' : 'orange'}>{results.top_match.overall_score}%</Badge>}</Tab>
                        <Tab><Icon as={FiShield} mr={2} /> Governance {results?.audit && <Badge ml={2} colorScheme={results.audit.passed_audit ? 'green' : 'red'}>{results.audit.passed_audit ? 'Pass' : 'Flag'}</Badge>}</Tab>
                        <Tab><Icon as={FiBook} mr={2} /> Upskilling</Tab>
                    </TabList>

                    <TabPanels>
                        {/* ANALYZE TAB */}
                        <TabPanel>
                            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                                <Card>
                                    <CardHeader pb={2}>
                                        <HStack><Icon as={FiUploadCloud} boxSize={5} color="blue.500" /><Heading size="md">Resume Input</Heading></HStack>
                                    </CardHeader>
                                    <CardBody>
                                        <VStack spacing={4} align="stretch">
                                            <Input ref={fileInputRef} type="file" accept=".txt,.pdf" onChange={handleFileUpload} display="none" />
                                            
                                            <Box 
                                                border="2px dashed" 
                                                borderColor={fileName ? 'green.400' : 'gray.300'} 
                                                borderRadius="xl" 
                                                p={6} 
                                                textAlign="center" 
                                                cursor="pointer" 
                                                onClick={() => fileInputRef.current?.click()} 
                                                _hover={{ borderColor: 'blue.400', bg: 'blue.50' }}
                                                bg={fileName ? 'green.50' : 'white'}
                                            >
                                                {fileName ? (
                                                    <VStack><Icon as={FiCheckCircle} boxSize={8} color="green.500" /><Text fontWeight="bold" color="green.600">{fileName}</Text></VStack>
                                                ) : (
                                                    <VStack><Icon as={FiUploadCloud} boxSize={8} color="gray.400" /><Text fontWeight="bold">Upload Resume</Text><Text fontSize="xs" color="gray.500">.txt or .pdf</Text></VStack>
                                                )}
                                            </Box>

                                            <Text fontSize="sm" color="gray.500" textAlign="center">— or paste text —</Text>

                                            <Textarea 
                                                placeholder="Paste resume content here..." 
                                                value={resumeText} 
                                                onChange={(e) => { setResumeText(e.target.value); setSelectedDemo(null); }} 
                                                minH="150px" 
                                                fontFamily="mono" 
                                                fontSize="sm" 
                                            />

                                            <HStack>
                                                <Button variant="ghost" size="sm" onClick={clearAll}>Clear</Button>
                                                <Spacer />
                                                {selectedDemo && <Badge colorScheme="purple">{DEMO_PROFILES.find(p => p.id === selectedDemo)?.name}</Badge>}
                                                <Text fontSize="xs" color="gray.400">{resumeText.length} chars</Text>
                                            </HStack>

                                            {resumeText && (
                                                <Box p={3} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" maxH="150px" overflowY="auto">
                                                    <Text fontSize="xs" fontWeight="bold" color="blue.600" mb={1}>PREVIEW</Text>
                                                    <Text fontSize="xs" whiteSpace="pre-wrap" color="gray.700">{resumeText.substring(0, 500)}{resumeText.length > 500 && '...'}</Text>
                                                </Box>
                                            )}
                                        </VStack>
                                    </CardBody>
                                </Card>

                                <Card>
                                    <CardHeader pb={2}><Heading size="md">Settings</Heading></CardHeader>
                                    <CardBody>
                                        <VStack spacing={5} align="stretch">
                                            <FormControl>
                                                <FormLabel>Target Job</FormLabel>
                                                <Select placeholder="Match against all jobs" value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)}>
                                                    {jobs.map((job) => (<option key={job.id} value={job.id}>{job.title} - {job.department}</option>))}
                                                </Select>
                                            </FormControl>

                                            <Alert status="info" borderRadius="md" py={2}>
                                                <AlertIcon as={FiDollarSign} />
                                                <Text fontSize="sm">Cost: <strong>${COST_PER_PROFILE}</strong> per analysis</Text>
                                            </Alert>

                                            <Button colorScheme="blue" size="lg" onClick={handleAnalyze} isLoading={loading} loadingText="Analyzing..." leftIcon={<FiZap />} isDisabled={!resumeText.trim()}>
                                                Analyze Resume
                                            </Button>

                                            {loading && <Progress size="sm" isIndeterminate colorScheme="blue" borderRadius="full" />}
                                        </VStack>
                                    </CardBody>
                                </Card>
                            </SimpleGrid>
                        </TabPanel>

                        {/* RESULTS TAB */}
                        <TabPanel>
                            {!results ? (
                                <Card><CardBody><VStack py={10}><Icon as={FiTarget} boxSize={12} color="gray.300" /><Text color="gray.500">No results yet. Run an analysis first.</Text></VStack></CardBody></Card>
                            ) : (
                                <VStack spacing={6} align="stretch">
                                    {isSafeMoment() && (
                                        <Alert status="warning" borderRadius="lg" variant="left-accent">
                                            <AlertIcon as={FiAlertOctagon} boxSize={8} />
                                            <Box><AlertTitle>Safety Check: Low Confidence</AlertTitle><AlertDescription>This profile has insufficient data. Recommend requesting more information before hiring decisions.</AlertDescription></Box>
                                        </Alert>
                                    )}

                                    <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6}>
                                        <Card><CardBody><Stat><StatLabel>Profile Confidence</StatLabel><StatNumber color={results.profile?.confidence_score >= 0.7 ? 'green.500' : 'orange.500'}>{Math.round((results.profile?.confidence_score || 0) * 100)}%</StatNumber><StatHelpText>{results.profile?.confidence_score >= 0.7 ? 'High' : 'Low'}</StatHelpText></Stat></CardBody></Card>
                                        <Card><CardBody><Stat><StatLabel>Top Match</StatLabel><StatNumber color={(results.top_match?.overall_score || 0) >= 70 ? 'green.500' : 'orange.500'}>{results.top_match?.overall_score || 0}%</StatNumber><StatHelpText>{results.top_match?.job_title || 'No match'}</StatHelpText></Stat></CardBody></Card>
                                        <Card><CardBody><Stat><StatLabel>Processing Time</StatLabel><StatNumber>{results.total_processing_time_ms || 0}ms</StatNumber><StatHelpText>Cost: ${COST_PER_PROFILE}</StatHelpText></Stat></CardBody></Card>
                                    </SimpleGrid>

                                    <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                                        <Card>
                                            <CardHeader pb={2}><Heading size="md">Parsed Profile</Heading></CardHeader>
                                            <CardBody>
                                                <SimpleGrid columns={3} spacing={4} mb={4}>
                                                    <Box textAlign="center" p={3} bg="gray.50" borderRadius="md"><Text fontSize="2xl" fontWeight="bold">{results.profile?.experience_years || '?'}</Text><Text fontSize="xs">Years Exp</Text></Box>
                                                    <Box textAlign="center" p={3} bg="gray.50" borderRadius="md"><Text fontSize="md" fontWeight="bold">{results.profile?.education_level || 'N/A'}</Text><Text fontSize="xs">Education</Text></Box>
                                                    <Box textAlign="center" p={3} bg="gray.50" borderRadius="md"><Text fontSize="2xl" fontWeight="bold">{results.profile?.skills?.length || 0}</Text><Text fontSize="xs">Skills</Text></Box>
                                                </SimpleGrid>
                                                <Wrap>{(results.profile?.skills || []).slice(0, 10).map((skill, idx) => (<WrapItem key={idx}><Tag size="sm" colorScheme="blue">{skill.name}</Tag></WrapItem>))}</Wrap>
                                            </CardBody>
                                        </Card>

                                        {results.top_match && (
                                            <Card>
                                                <CardHeader pb={2}><HStack><Heading size="md">Top Match</Heading><Badge colorScheme={results.top_match.competency_level === 'strong' ? 'green' : 'yellow'}>{results.top_match.competency_level}</Badge></HStack></CardHeader>
                                                <CardBody>
                                                    <HStack justify="space-between" mb={4}>
                                                        <Text fontSize="lg" fontWeight="bold">{results.top_match.job_title}</Text>
                                                        <CircularProgress value={results.top_match.overall_score} color={results.top_match.overall_score >= 70 ? 'green.400' : 'orange.400'} size="60px"><CircularProgressLabel fontWeight="bold">{results.top_match.overall_score}%</CircularProgressLabel></CircularProgress>
                                                    </HStack>
                                                    <SimpleGrid columns={2} spacing={3}>
                                                        {['Skills', 'Experience', 'Education', 'Achievements'].map((label, i) => {
                                                            const scores = [results.top_match.skills_match_score, results.top_match.experience_match_score, results.top_match.education_match_score, results.top_match.achievement_match_score];
                                                            return (
                                                                <Box key={label}><HStack justify="space-between" mb={1}><Text fontSize="sm">{label}</Text><Text fontSize="sm" fontWeight="bold">{scores[i]}/10</Text></HStack><Progress value={scores[i] * 10} colorScheme="blue" size="sm" borderRadius="full" /></Box>
                                                            );
                                                        })}
                                                    </SimpleGrid>
                                                    {results.top_match.skill_transfers?.length > 0 && <Button mt={4} size="sm" variant="outline" leftIcon={<FiArrowRight />} onClick={onTransferOpen} width="100%">View Skill Transfers</Button>}
                                                </CardBody>
                                            </Card>
                                        )}

                                        {results.top_match && <Card><CardHeader pb={2}><Heading size="md">Skill Gap Radar</Heading></CardHeader><CardBody><Box h="250px"><Radar data={getRadarData(results.top_match)} options={radarOptions} /></Box></CardBody></Card>}
                                        {results.matches?.length > 1 && <Card><CardHeader pb={2}><Heading size="md">All Matches</Heading></CardHeader><CardBody><Box h="250px"><Bar data={getScoreDistribution()} options={barOptions} /></Box></CardBody></Card>}
                                    </SimpleGrid>
                                </VStack>
                            )}
                        </TabPanel>

                        {/* GOVERNANCE TAB */}
                        <TabPanel>
                            {!results?.audit ? (
                                <Card><CardBody><VStack py={10}><Icon as={FiShield} boxSize={12} color="gray.300" /><Text color="gray.500">No audit results yet</Text></VStack></CardBody></Card>
                            ) : (
                                <VStack spacing={6} align="stretch">
                                    <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6}>
                                        <Card bg={results.audit.passed_audit ? 'green.50' : 'orange.50'}><CardBody><HStack><Icon as={results.audit.passed_audit ? FiCheckCircle : FiAlertTriangle} boxSize={10} color={results.audit.passed_audit ? 'green.500' : 'orange.500'} /><Box><Text fontWeight="bold" fontSize="lg">{results.audit.passed_audit ? 'Audit Passed' : 'Flagged'}</Text><Text fontSize="sm">Fairness: {results.audit.fairness_score}%</Text></Box></HStack></CardBody></Card>
                                        <Card><CardBody><Stat><StatLabel>Bias Flags</StatLabel><StatNumber color={results.audit.bias_flags?.length > 0 ? 'orange.500' : 'green.500'}>{results.audit.bias_flags?.length || 0}</StatNumber></Stat></CardBody></Card>
                                        <Card><CardBody><Button leftIcon={<FiDownload />} onClick={exportAuditLog} colorScheme="blue" variant="outline" w="100%">Download Audit Log</Button></CardBody></Card>
                                    </SimpleGrid>

                                    <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                                        <Card>
                                            <CardHeader pb={2}><Heading size="md">Bias Flags</Heading></CardHeader>
                                            <CardBody>
                                                {(results.audit.bias_flags?.length || 0) === 0 ? (
                                                    <Alert status="success" borderRadius="md"><AlertIcon />No bias detected</Alert>
                                                ) : (
                                                    <Accordion allowMultiple>
                                                        {results.audit.bias_flags.map((flag, idx) => (
                                                            <AccordionItem key={idx}><AccordionButton><HStack flex="1"><Badge colorScheme={flag.severity === 'high' ? 'red' : 'orange'}>{flag.severity}</Badge><Text>{flag.category}</Text></HStack><AccordionIcon /></AccordionButton><AccordionPanel><Text fontSize="sm">{flag.indicator}</Text><Text fontSize="sm" mt={2} color="blue.600">{flag.recommendation}</Text></AccordionPanel></AccordionItem>
                                                        ))}
                                                    </Accordion>
                                                )}
                                            </CardBody>
                                        </Card>
                                        <Card>
                                            <CardHeader pb={2}><Heading size="md">Decision Log</Heading></CardHeader>
                                            <CardBody><Box bg="gray.900" color="green.300" p={4} borderRadius="md" fontFamily="mono" fontSize="xs" whiteSpace="pre-wrap" maxH="300px" overflowY="auto">{results.audit.decision_log || 'No log'}</Box></CardBody>
                                        </Card>
                                    </SimpleGrid>
                                </VStack>
                            )}
                        </TabPanel>

                        {/* UPSKILLING TAB */}
                        <TabPanel>
                            {!results?.upskill_path ? (
                                <Card><CardBody><VStack py={10}><Icon as={FiBook} boxSize={12} color="gray.300" /><Text color="gray.500">No upskilling recommendations yet</Text></VStack></CardBody></Card>
                            ) : (
                                <VStack spacing={6} align="stretch">
                                    <SimpleGrid columns={{ base: 1, lg: 4 }} spacing={6}>
                                        <Card bg="green.50"><CardBody><Stat><StatLabel>Quick Wins</StatLabel><StatNumber color="green.600">{results.upskill_path.quick_wins?.length || 0}</StatNumber><StatHelpText>1-2 weeks each</StatHelpText></Stat></CardBody></Card>
                                        <Card bg="purple.50"><CardBody><Stat><StatLabel>Core Learning</StatLabel><StatNumber color="purple.600">{results.upskill_path.core_learning?.length || 0}</StatNumber><StatHelpText>1-2 months each</StatHelpText></Stat></CardBody></Card>
                                        <Card bg="blue.50"><CardBody><Stat><StatLabel>Total Time</StatLabel><StatNumber color="blue.600">~{results.upskill_path.total_time_weeks || 0} weeks</StatNumber></Stat></CardBody></Card>
                                        <Card bg="orange.50"><CardBody><Stat><StatLabel>Est. Cost</StatLabel><StatNumber color="orange.600">~${((results.upskill_path.quick_wins?.length || 0) * 30 + (results.upskill_path.core_learning?.length || 0) * 100)}</StatNumber></Stat></CardBody></Card>
                                    </SimpleGrid>

                                    <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                                        <Card><CardHeader pb={2}><HStack><Icon as={FiClock} color="green.500" /><Heading size="md">Quick Wins</Heading></HStack></CardHeader><CardBody><VStack align="stretch" spacing={2}>{(results.upskill_path.quick_wins || []).map((r, idx) => (<Box key={idx} p={3} bg="green.50" borderRadius="md" borderLeft="4px solid" borderColor="green.400"><Text fontWeight="bold" fontSize="sm">{r.title}</Text><Badge colorScheme="green" fontSize="xs">{r.provider}</Badge></Box>))}</VStack></CardBody></Card>
                                        <Card><CardHeader pb={2}><HStack><Icon as={FiAward} color="purple.500" /><Heading size="md">Core Learning</Heading></HStack></CardHeader><CardBody><VStack align="stretch" spacing={2}>{(results.upskill_path.core_learning || []).map((r, idx) => (<Box key={idx} p={3} bg="purple.50" borderRadius="md" borderLeft="4px solid" borderColor="purple.400"><Text fontWeight="bold" fontSize="sm">{r.title}</Text><Badge colorScheme="purple" fontSize="xs">{r.provider}</Badge></Box>))}</VStack></CardBody></Card>
                                    </SimpleGrid>
            </VStack>
                            )}
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Container>

            {/* Skill Transfer Modal */}
            <Modal isOpen={isTransferOpen} onClose={onTransferClose} size="xl">
                <ModalOverlay />
                <ModalContent><ModalHeader>Skill Transfer Analysis</ModalHeader><ModalCloseButton />
                    <ModalBody pb={6}>
                        <TableContainer><Table size="sm"><Thead><Tr><Th>Candidate Skill</Th><Th>Job Requirement</Th><Th isNumeric>Transfer %</Th></Tr></Thead><Tbody>{(results?.top_match?.skill_transfers || []).map((t, idx) => (<Tr key={idx}><Td>{t.candidate_skill}</Td><Td>{t.job_requirement}</Td><Td isNumeric><Badge colorScheme={t.transfer_efficiency >= 70 ? 'green' : 'orange'}>{t.transfer_efficiency}%</Badge></Td></Tr>))}</Tbody></Table></TableContainer>
                    </ModalBody>
                </ModalContent>
            </Modal>

            {/* Summary Modal */}
            <Modal isOpen={isSummaryOpen} onClose={onSummaryClose} size="xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader bg="blue.600" color="white" borderTopRadius="md">Analysis Summary</ModalHeader>
                    <ModalCloseButton color="white" />
                    <ModalBody py={6}>
                        {results && (
                            <SimpleGrid columns={3} spacing={4}>
                                <Box textAlign="center" p={4} bg="blue.50" borderRadius="md"><Text fontSize="3xl" fontWeight="bold" color="blue.600">{results.top_match?.overall_score || 0}%</Text><Text fontSize="sm">Match Score</Text></Box>
                                <Box textAlign="center" p={4} bg="green.50" borderRadius="md"><Text fontSize="3xl" fontWeight="bold" color="green.600">{results.audit?.fairness_score || 0}%</Text><Text fontSize="sm">Fairness</Text></Box>
                                <Box textAlign="center" p={4} bg="purple.50" borderRadius="md"><Text fontSize="3xl" fontWeight="bold" color="purple.600">{Math.round((results.profile?.confidence_score || 0) * 100)}%</Text><Text fontSize="sm">Confidence</Text></Box>
                            </SimpleGrid>
                        )}
                    </ModalBody>
                    <ModalFooter><Button colorScheme="blue" onClick={onSummaryClose}>Close</Button></ModalFooter>
                </ModalContent>
            </Modal>

            {/* Footer */}
            <Box bg="white" borderTop="1px" borderColor="gray.200" py={3} mt={8}>
                <Container maxW="container.xl">
                    <Flex align="center" fontSize="sm" color="gray.500">
                        <Text>LucidMatch - EY AI Case Competition 2026</Text>
                        <Spacer />
                        <HStack spacing={4}><Text>{analysisCount} profiles analyzed</Text><Text>Cost: ${(analysisCount * COST_PER_PROFILE).toFixed(2)}</Text></HStack>
                    </Flex>
                </Container>
            </Box>
        </Box>
    );
}

export default App;
