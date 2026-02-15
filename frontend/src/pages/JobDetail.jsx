import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Button, Icon, Table, Thead, Tbody, Tr, Th, Td, Badge, Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton, DrawerHeader, DrawerBody, Progress, HStack, VStack, useDisclosure, Tabs, TabList, TabPanels, Tab, TabPanel, Code, Checkbox, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, Skeleton, AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogContent, AlertDialogOverlay, IconButton, useToast } from '@chakra-ui/react'
import { useParams } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import apiClient from '../api/client'
import SkillRadar from '../components/SkillRadar'
import { AlertCircle, CheckCircle2, BookOpen, Search, Terminal, Activity, Swords, Trash2, FileText } from 'lucide-react'

const JobDetail = () => {
    const { id } = useParams()
    const [job, setJob] = useState(null)
    const [candidates, setCandidates] = useState([])
    const [selectedCandidate, setSelectedCandidate] = useState(null)
    const [compareSelection, setCompareSelection] = useState([])
    const [comparisonData, setComparisonData] = useState(null)
    const [isComparing, setIsComparing] = useState(false)
    const [deleteId, setDeleteId] = useState(null)
    const [isDeleting, setIsDeleting] = useState(false)
    const cancelRef = useRef()
    const toast = useToast()

    // Disclosures
    const { isOpen: isDrawerOpen, onOpen: onDrawerOpen, onClose: onDrawerClose } = useDisclosure()
    const { isOpen: isModalOpen, onOpen: onModalOpen, onClose: onModalClose } = useDisclosure()
    const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()
    const { isOpen: isResumeOpen, onOpen: onResumeOpen, onClose: onResumeClose } = useDisclosure()
    const { isOpen: isAuditOpen, onOpen: onAuditOpen, onClose: onAuditClose } = useDisclosure()
    const [isJobDetailsOpen, setIsJobDetailsOpen] = useState(false)
    const [resumeText, setResumeText] = useState(null)
    const [demoMode, setDemoMode] = useState(() => {
        return localStorage.getItem('demoMode') === 'true'
    })

    // Listen for demo mode changes from other pages
    useEffect(() => {
        const handleStorageChange = () => {
            setDemoMode(localStorage.getItem('demoMode') === 'true')
        }
        window.addEventListener('storage', handleStorageChange)
        return () => window.removeEventListener('storage', handleStorageChange)
    }, [])

    useEffect(() => {
        const fetchJob = async () => {
            try {
                const res = await apiClient.get(`/api/jobs/${id}`)
                setJob(res.data.job)
                setCandidates(res.data.candidates)
            } catch (error) {
                console.error("Failed to fetch job", error)
            }
        }
        fetchJob()
    }, [id])

    const handleViewCandidate = (candidate) => {
        const data = JSON.parse(candidate.raw_json)
        const logs = candidate.agent_logs ? JSON.parse(candidate.agent_logs) : []
        setSelectedCandidate({ ...candidate, ...data, logs })
        onDrawerOpen()
    }

    const handleViewResume = (candidate) => {
        try {
            const data = JSON.parse(candidate.raw_json)
            setResumeText(data.resume_text || "No resume text available for this candidate.")
        } catch (e) {
            setResumeText("Error loading resume text.")
        }
        onResumeOpen()
    }

    const toggleCompare = (id) => {
        if (compareSelection.includes(id)) {
            setCompareSelection(prev => prev.filter(cid => cid !== id))
        } else {
            if (compareSelection.length < 2) {
                setCompareSelection(prev => [...prev, id])
            }
        }
    }

    const runComparison = async () => {
        setIsComparing(true)
        onModalOpen()
        try {
            const res = await apiClient.post('/api/compare', {
                candidate_id_1: compareSelection[0],
                candidate_id_2: compareSelection[1]
            })
            setComparisonData(res.data)
        } catch (error) {
            console.error("Comparison failed", error)
        } finally {
            setIsComparing(false)
        }
    }

    const confirmDelete = (candidateId) => {
        setDeleteId(candidateId)
        onDeleteOpen()
    }

    const handleDelete = async () => {
        setIsDeleting(true)
        try {
            await apiClient.delete(`/api/analyses/${deleteId}`)
            setCandidates(prev => prev.filter(c => c.id !== deleteId))
            toast({
                title: "Applicant deleted",
                description: "The candidate has been removed from this job.",
                status: "success",
                duration: 3000,
                isClosable: true,
            })
        } catch (error) {
            console.error("Delete failed", error)
            toast({
                title: "Delete failed",
                description: "Could not delete this applicant.",
                status: "error",
                duration: 3000,
                isClosable: true,
            })
        } finally {
            setIsDeleting(false)
            setDeleteId(null)
            onDeleteClose()
        }
    }

    if (!job) return (
        <Stack spacing={8}>
            <HStack justify="space-between">
                <Box>
                    <Skeleton height="32px" width="300px" mb={2} />
                    <Skeleton height="20px" width="200px" />
                </Box>
            </HStack>
            <Card overflow="hidden">
                <Table variant="simple">
                    <Thead bg="slate.50">
                        <Tr>
                            <Th w="50px"></Th>
                            <Th>Rank</Th>
                            <Th>Candidate</Th>
                            <Th isNumeric>Match Score</Th>
                            <Th>Status</Th>
                            <Th>Action</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {[1, 2, 3].map((i) => (
                            <Tr key={i}>
                                <Td><Skeleton height="20px" width="20px" /></Td>
                                <Td><Skeleton height="20px" width="30px" /></Td>
                                <Td><Skeleton height="20px" width="150px" /></Td>
                                <Td><Skeleton height="20px" width="50px" /></Td>
                                <Td><Skeleton height="20px" width="60px" /></Td>
                                <Td><Skeleton height="30px" width="80px" /></Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Card>
        </Stack>
    )

    return (
        <Stack spacing={8}>
            <HStack justify="space-between">
                <Box>
                    <Heading size="lg" mb={1}>{job.title}</Heading>
                    <HStack>
                        <Badge colorScheme="brand">{job.department}</Badge>
                        <Text color="slate.500">- {candidates.length} Candidates</Text>
                        <Button size="xs" variant="outline" leftIcon={<Icon as={BookOpen} />} onClick={() => setIsJobDetailsOpen(true)}>
                            View Job Details
                        </Button>
                    </HStack>
                </Box>
                {compareSelection.length === 2 && (
                    <Button leftIcon={<Icon as={Swords} />} colorScheme="purple" onClick={runComparison}>
                        Compare Selected (2)
                    </Button>
                )}
            </HStack>

            <Card overflow="hidden">
                <Table variant="simple">
                    <Thead bg="slate.50">
                        <Tr>
                            <Th w="50px"></Th>
                            <Th>Rank</Th>
                            <Th>Candidate</Th>
                            <Th isNumeric>Match Score</Th>
                            <Th>Status</Th>
                            <Th>Action</Th>
                            <Th w="50px"></Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {candidates.map((c, index) => (
                            <Tr key={c.id} _hover={{ bg: 'brand.50' }} transition="all 0.1s">
                                <Td>
                                    <Checkbox
                                        isChecked={compareSelection.includes(c.id)}
                                        onChange={() => toggleCompare(c.id)}
                                        isDisabled={!compareSelection.includes(c.id) && compareSelection.length >= 2}
                                        colorScheme="purple"
                                    />
                                </Td>
                                <Td fontWeight="bold" color="slate.400">#{index + 1}</Td>
                                <Td>
                                    <Stack spacing={1}>
                                        <Text fontWeight="medium">{c.candidate_name}</Text>
                                        {demoMode && c.test_metadata && (() => {
                                            try {
                                                const testInfo = typeof c.test_metadata === 'string'
                                                    ? JSON.parse(c.test_metadata)
                                                    : c.test_metadata
                                                return (
                                                    <Badge colorScheme="purple" fontSize="xs" maxW="300px">
                                                        {testInfo.demo_label || testInfo.test_name}
                                                    </Badge>
                                                )
                                            } catch (e) {
                                                return null
                                            }
                                        })()}
                                    </Stack>
                                </Td>
                                <Td isNumeric>
                                    <Badge colorScheme={c.match_score > 75 ? 'green' : c.match_score > 50 ? 'yellow' : 'red'} fontSize="0.9em">
                                        {c.match_score}%
                                    </Badge>
                                </Td>
                                <Td><Badge variant="outline">New</Badge></Td>
                                <Td>
                                    <HStack spacing={1}>
                                        <IconButton
                                            icon={<Icon as={FileText} />}
                                            size="sm"
                                            variant="ghost"
                                            colorScheme="blue"
                                            aria-label="View Resume"
                                            onClick={() => handleViewResume(c)}
                                        />
                                        <Button size="sm" variant="ghost" colorScheme="brand" onClick={() => handleViewCandidate(c)}>
                                            Analyze
                                        </Button>
                                    </HStack>
                                </Td>
                                <Td>
                                    <IconButton
                                        icon={<Icon as={Trash2} />}
                                        size="sm"
                                        variant="ghost"
                                        colorScheme="red"
                                        aria-label="Delete applicant"
                                        onClick={() => confirmDelete(c.id)}
                                    />
                                </Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Card>

            {/* Job Details Modal */}
            <Modal isOpen={isJobDetailsOpen} onClose={() => setIsJobDetailsOpen(false)} size="xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Job Details</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <Stack spacing={4}>
                            <Box>
                                <Heading size="sm" mb={2} color="slate.700">Description</Heading>
                                <Text color="slate.600" whiteSpace="pre-wrap">{job.description}</Text>
                            </Box>
                            <Box>
                                <Heading size="sm" mb={2} color="slate.700">Requirements</Heading>
                                <Text color="slate.600" whiteSpace="pre-wrap">{job.requirements}</Text>
                            </Box>
                        </Stack>
                    </ModalBody>
                </ModalContent>
            </Modal>

            {/* Deep Dive Drawer */}
            <Drawer isOpen={isDrawerOpen} placement="right" onClose={onDrawerClose} size="xl">
                <DrawerOverlay />
                <DrawerContent>
                    <DrawerCloseButton />
                    <DrawerHeader borderBottomWidth="1px">Glass Box Analysis</DrawerHeader>
                    <DrawerBody p={0}>
                        {selectedCandidate && (
                            <Tabs isFitted variant="enclosed">
                                <TabList mb="1em" borderBottomWidth="1px" borderColor="slate.200" bg="slate.50" pt={2} px={2}>
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Overview</Tab>
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Decision Details</Tab>
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Evidence</Tab>
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Neural Logs</Tab>
                                </TabList>

                                <TabPanels>
                                    {/* 1. OVERVIEW PANEL */}
                                    <TabPanel>
                                        <Stack spacing={6} p={4}>
                                            {/* Demo Mode Test Info */}
                                            {demoMode && selectedCandidate?.test_metadata && (() => {
                                                try {
                                                    const testInfo = typeof selectedCandidate.test_metadata === 'string'
                                                        ? JSON.parse(selectedCandidate.test_metadata)
                                                        : selectedCandidate.test_metadata

                                                    return (
                                                        <Card bg="purple.50" borderColor="purple.400" borderWidth="3px">
                                                            <CardBody>
                                                                <Stack spacing={4}>
                                                                    <HStack align="start">
                                                                        <Icon as={Terminal} color="purple.600" boxSize={6} />
                                                                        <Box flex="1">
                                                                            <Badge colorScheme="purple" fontSize="xs" mb={2}>DEMO MODE</Badge>
                                                                            <Heading size="md" color="purple.800">
                                                                                {testInfo.demo_label || testInfo.test_name || "Test Scenario"}
                                                                            </Heading>
                                                                        </Box>
                                                                    </HStack>
                                                                    {testInfo.purpose && (
                                                                        <Box>
                                                                            <Text fontSize="xs" fontWeight="bold" color="purple.700" mb={1}>What We're Testing:</Text>
                                                                            <Text fontSize="sm">{testInfo.purpose}</Text>
                                                                        </Box>
                                                                    )}
                                                                    {testInfo.success_criteria && (
                                                                        <Box>
                                                                            <Text fontSize="xs" fontWeight="bold" color="purple.700" mb={1}>Success Looks Like:</Text>
                                                                            <Text fontSize="sm" whiteSpace="pre-wrap">{testInfo.success_criteria}</Text>
                                                                        </Box>
                                                                    )}
                                                                </Stack>
                                                            </CardBody>
                                                        </Card>
                                                    )
                                                } catch (e) {
                                                    return null
                                                }
                                            })()}
                                            <SimpleGrid columns={3} spacing={4}>
                                                <Card bg="brand.50" variant="outline" borderColor="brand.100">
                                                    <CardBody p={4} textAlign="center">
                                                        <Text fontSize="xs" color="brand.600" textTransform="uppercase" fontWeight="bold">Match Score</Text>
                                                        <Heading size="2xl" color="brand.700">{selectedCandidate.match.match_score}%</Heading>
                                                    </CardBody>
                                                </Card>
                                                <Card variant="outline">
                                                    <CardBody p={4} textAlign="center">
                                                        <Text fontSize="xs" color="slate.500" textTransform="uppercase" fontWeight="bold">Fairness</Text>
                                                        <Heading size="lg" mt={2} color="slate.700">{selectedCandidate.audit.fairness_score}%</Heading>
                                                    </CardBody>
                                                </Card>
                                                <Card variant="outline">
                                                    <CardBody p={4} textAlign="center">
                                                        <Text fontSize="xs" color="slate.500" textTransform="uppercase" fontWeight="bold">Status</Text>
                                                        <HStack justify="center" mt={2}>
                                                            <Icon as={selectedCandidate.audit.flagged ? AlertCircle : CheckCircle2} color={selectedCandidate.audit.flagged ? "red.500" : "green.500"} />
                                                            <Text fontWeight="bold">{selectedCandidate.audit.flagged ? "Flagged" : "Clean"}</Text>
                                                        </HStack>
                                                        {selectedCandidate.audit.flagged && (
                                                            <Button size="xs" mt={2} colorScheme="red" variant="outline" onClick={onAuditOpen}>
                                                                View Details
                                                            </Button>
                                                        )}
                                                    </CardBody>
                                                </Card>
                                            </SimpleGrid>

                                            <Box>
                                                <Heading size="sm" mb={3}>Reasoning Trace</Heading>
                                                <Text fontSize="sm" color="slate.600" lineHeight="relaxed">
                                                    {selectedCandidate.match.reasoning}
                                                </Text>
                                            </Box>

                                            <Box h="250px" border="1px" borderColor="slate.200" borderRadius="xl" p={4}>
                                                <SkillRadar data={selectedCandidate.match.radar_chart_data || []} />
                                            </Box>
                                        </Stack>
                                    </TabPanel>

                                    {/* 2. DECISION DETAILS PANEL */}
                                    <TabPanel>
                                        <Stack spacing={6} p={4}>
                                            <Box>
                                                <Heading size="md" mb={2}>10-Criteria Evaluation</Heading>
                                                <Text color="slate.500">Detailed breakdown of how this candidate was scored on each dimension.</Text>
                                            </Box>

                                            {selectedCandidate.match?.criteria_scores && Object.entries(selectedCandidate.match.criteria_scores).map(([key, criterion]) => {
                                                const score = criterion.score || criterion.potential_score || 0
                                                const level = criterion.level || criterion.potential_level || 'Low'
                                                const levelColor = level === 'High' ? 'green' : level === 'Medium' ? 'yellow' : 'red'

                                                return (
                                                    <Card key={key} variant="outline" borderLeftWidth="4px" borderLeftColor={`${levelColor}.400`}>
                                                        <CardBody>
                                                            <HStack justify="space-between" mb={3}>
                                                                <Heading size="sm" textTransform="capitalize">
                                                                    {key.replace(/_/g, ' ')}
                                                                </Heading>
                                                                <HStack>
                                                                    <Badge colorScheme={levelColor}>{level}</Badge>
                                                                    <Text fontWeight="bold" fontSize="lg" color={`${levelColor}.600`}>
                                                                        {score}/10
                                                                    </Text>
                                                                </HStack>
                                                            </HStack>

                                                            <Progress
                                                                value={score * 10}
                                                                colorScheme={levelColor}
                                                                size="sm"
                                                                borderRadius="full"
                                                                mb={3}
                                                            />

                                                            {criterion.evidence && (
                                                                <Box mb={3} p={3} bg="slate.50" borderRadius="md">
                                                                    <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={1}>EVIDENCE</Text>
                                                                    <Text fontSize="sm" color="slate.700">{criterion.evidence}</Text>
                                                                </Box>
                                                            )}

                                                            {criterion.justification && (
                                                                <Box mb={3}>
                                                                    <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={1}>JUSTIFICATION</Text>
                                                                    <Text fontSize="sm" color="slate.600">{criterion.justification}</Text>
                                                                </Box>
                                                            )}

                                                            {/* Skills lists for specific criteria */}
                                                            {criterion.technical_skills_matched?.length > 0 && (
                                                                <HStack wrap="wrap" spacing={2} mb={2}>
                                                                    <Text fontSize="xs" fontWeight="bold" color="green.600">[OK] Technical:</Text>
                                                                    {criterion.technical_skills_matched.map((skill, i) => (
                                                                        <Badge key={i} colorScheme="green" variant="subtle" size="sm">{skill}</Badge>
                                                                    ))}
                                                                </HStack>
                                                            )}

                                                            {criterion.soft_skills_matched?.length > 0 && (
                                                                <HStack wrap="wrap" spacing={2} mb={2}>
                                                                    <Text fontSize="xs" fontWeight="bold" color="blue.600">[OK] Soft Skills:</Text>
                                                                    {criterion.soft_skills_matched.map((skill, i) => (
                                                                        <Badge key={i} colorScheme="blue" variant="subtle" size="sm">{skill}</Badge>
                                                                    ))}
                                                                </HStack>
                                                            )}

                                                            {criterion.required_gaps?.length > 0 && (
                                                                <HStack wrap="wrap" spacing={2} mb={2}>
                                                                    <Text fontSize="xs" fontWeight="bold" color="red.600">[GAP] Required Gaps:</Text>
                                                                    {criterion.required_gaps.map((gap, i) => (
                                                                        <Badge key={i} colorScheme="red" variant="subtle" size="sm">{gap}</Badge>
                                                                    ))}
                                                                </HStack>
                                                            )}

                                                            {criterion.skills_identified?.length > 0 && (
                                                                <HStack wrap="wrap" spacing={2} mb={2}>
                                                                    <Text fontSize="xs" fontWeight="bold" color="purple.600">Trainable:</Text>
                                                                    {criterion.skills_identified.map((skill, i) => (
                                                                        <Badge key={i} colorScheme="purple" variant="subtle" size="sm">{skill}</Badge>
                                                                    ))}
                                                                </HStack>
                                                            )}

                                                            {/* Special display for potential/readiness */}
                                                            {key === 'potential_readiness' && (
                                                                <SimpleGrid columns={2} spacing={4} mt={3}>
                                                                    <Box p={3} bg="purple.50" borderRadius="md" textAlign="center">
                                                                        <Text fontSize="xs" fontWeight="bold" color="purple.600">POTENTIAL</Text>
                                                                        <Text fontSize="xl" fontWeight="bold" color="purple.700">{criterion.potential_score}/10</Text>
                                                                    </Box>
                                                                    <Box p={3} bg="green.50" borderRadius="md" textAlign="center">
                                                                        <Text fontSize="xs" fontWeight="bold" color="green.600">READINESS</Text>
                                                                        <Text fontSize="xl" fontWeight="bold" color="green.700">{criterion.readiness_score}/10</Text>
                                                                    </Box>
                                                                </SimpleGrid>
                                                            )}
                                                        </CardBody>
                                                    </Card>
                                                )
                                            })}

                                            {!selectedCandidate.match?.criteria_scores && (
                                                <Text color="slate.400">No detailed criteria scores available.</Text>
                                            )}
                                        </Stack>
                                    </TabPanel>

                                    {/* 3. EVIDENCE PANEL */}
                                    <TabPanel>
                                        <Stack spacing={6} p={4}>
                                            <Heading size="md">Evidence & Citations</Heading>
                                            <Text color="slate.500">The AI extracted these specific quotes to verify skills.</Text>

                                            <Stack spacing={4}>
                                                {selectedCandidate.match.evidence?.map((item, i) => (
                                                    <Card key={i} variant="outline" borderLeftWidth="4px" borderLeftColor="brand.500">
                                                        <CardBody py={3}>
                                                            <HStack justify="space-between" mb={2}>
                                                                <Badge colorScheme="brand">{item.requirement}</Badge>
                                                                <Text fontSize="xs" fontWeight="bold" color="green.600">Relevance: {item.score}%</Text>
                                                            </HStack>
                                                            <HStack align="start">
                                                                <Icon as={Search} boxSize={4} color="slate.400" mt={1} />
                                                                <Text fontStyle="italic" color="slate.700" fontSize="sm">
                                                                    "{item.quote}"
                                                                </Text>
                                                            </HStack>
                                                        </CardBody>
                                                    </Card>
                                                ))}
                                                {(!selectedCandidate.match.evidence || selectedCandidate.match.evidence.length === 0) && (
                                                    <Text color="slate.400">No specific evidence citations available for this run.</Text>
                                                )}
                                            </Stack>
                                        </Stack>
                                    </TabPanel>

                                    {/* 3. NEURAL LOGS PANEL */}
                                    <TabPanel>
                                        <Stack spacing={6} p={4}>
                                            <HStack justify="space-between">
                                                <Heading size="md">Black Box Recorder</Heading>
                                                <Badge colorScheme="purple" variant="solid"><Icon as={Terminal} size={12} style={{ display: 'inline', marginRight: '4px' }} /> SYSTEM LOGS</Badge>
                                            </HStack>
                                            <Text color="slate.500">Raw timeline of agent inputs and outputs.</Text>

                                            <Stack spacing={0} borderLeftWidth="2px" borderColor="slate.200" ml={3}>
                                                {selectedCandidate.logs && selectedCandidate.logs.map((log, i) => (
                                                    <Box key={i} position="relative" pb={8} pl={8}>
                                                        <Box position="absolute" left="-9px" top="0" boxSize="16px" borderRadius="full" bg="white" borderWidth="4px" borderColor="brand.500" />

                                                        <Stack spacing={2}>
                                                            <HStack>
                                                                <Text fontWeight="bold" color="brand.700">{log.agent}</Text>
                                                                <Text fontSize="xs" color="slate.400">{new Date(log.timestamp).toLocaleTimeString()}</Text>
                                                            </HStack>

                                                            <Box>
                                                                <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={1}>PROMPT (INPUT)</Text>
                                                                <Code display="block" whiteSpace="pre-wrap" p={2} borderRadius="md" fontSize="xs" maxH="150px" overflowY="auto">
                                                                    {log.input}
                                                                </Code>
                                                            </Box>

                                                            <Box>
                                                                <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={1}>COMPLETION (OUTPUT)</Text>
                                                                <Code display="block" whiteSpace="pre-wrap" p={2} borderRadius="md" bg="slate.900" color="green.300" fontSize="xs" maxH="200px" overflowY="auto">
                                                                    {log.output}
                                                                </Code>
                                                            </Box>
                                                        </Stack>
                                                    </Box>
                                                ))}
                                                {(!selectedCandidate.logs || selectedCandidate.logs.length === 0) && (
                                                    <Text pl={8} color="slate.400">No logs captured. Run a new analysis to see neural data.</Text>
                                                )}
                                            </Stack>
                                        </Stack>
                                    </TabPanel>
                                </TabPanels>
                            </Tabs>
                        )}
                    </DrawerBody>
                </DrawerContent>
            </Drawer>

            {/* Comparative Analysis Modal */}
            <Modal isOpen={isModalOpen} onClose={onModalClose} size="4xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader bg="purple.50" borderBottomWidth="1px" borderColor="purple.100">
                        <HStack>
                            <Icon as={Swords} color="purple.600" />
                            <Text color="purple.800">Head-to-Head Analysis</Text>
                        </HStack>
                    </ModalHeader>
                    <ModalCloseButton />
                    <ModalBody p={6}>
                        {isComparing && (
                            <VStack py={12}>
                                <Text className="animate-pulse" color="purple.600" fontWeight="bold">To The Arena...</Text>
                                <Progress size="xs" isIndeterminate colorScheme="purple" w="200px" borderRadius="full" mt={4} />
                            </VStack>
                        )}

                        {!isComparing && comparisonData && (
                            <Stack spacing={8}>
                                <Card variant="filled" bg="purple.50">
                                    <CardBody>
                                        <Heading size="sm" color="purple.900" mb={2}>The Verdict</Heading>
                                        <Text fontSize="lg" fontWeight="medium" color="purple.800">
                                            {comparisonData.verdict}
                                        </Text>
                                    </CardBody>
                                </Card>

                                <SimpleGrid columns={2} spacing={8}>
                                    <Box>
                                        <Heading size="sm" mb={4} color="slate.700">Detailed Breakdown</Heading>
                                        <VStack align="stretch" spacing={3}>
                                            {comparisonData.comparison_points?.map((point, i) => (
                                                <HStack key={i} justify="space-between" p={3} bg="white" borderRadius="md" borderWidth="1px" borderColor="slate.200">
                                                    <Text fontSize="sm" fontWeight="bold" color="slate.600">{point.dimension}</Text>
                                                    <Badge colorScheme={point.winner === 'A' ? 'blue' : 'orange'}>
                                                        Winner: Candidate {point.winner}
                                                    </Badge>
                                                </HStack>
                                            ))}
                                        </VStack>
                                    </Box>

                                    <Box>
                                        <Heading size="sm" mb={4} color="slate.700">Key Advantages</Heading>
                                        <Stack spacing={2}>
                                            <Text fontSize="xs" fontWeight="bold" color="blue.600">CANDIDATE A</Text>
                                            <VStack align="start" spacing={1} pl={2} borderLeft="2px" borderColor="blue.200" mb={4}>
                                                {comparisonData.advantage_a?.map((adv, i) => (
                                                    <Text key={i} fontSize="sm" color="slate.600">- {adv}</Text>
                                                ))}
                                            </VStack>

                                            <Text fontSize="xs" fontWeight="bold" color="orange.600">CANDIDATE B</Text>
                                            <VStack align="start" spacing={1} pl={2} borderLeft="2px" borderColor="orange.200">
                                                {comparisonData.advantage_b?.map((adv, i) => (
                                                    <Text key={i} fontSize="sm" color="slate.600">- {adv}</Text>
                                                ))}
                                            </VStack>
                                        </Stack>
                                    </Box>
                                </SimpleGrid>
                            </Stack>
                        )}
                    </ModalBody>
                </ModalContent>
            </Modal>

            {/* Resume Text Modal */}
            <Modal isOpen={isResumeOpen} onClose={onResumeClose} size="xl" scrollBehavior="inside">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Original Resume</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <Box p={4} bg="slate.50" borderRadius="md" borderWidth="1px" borderColor="slate.200">
                            <Text whiteSpace="pre-wrap" fontSize="sm" fontFamily="mono" color="slate.700">
                                {resumeText}
                            </Text>
                        </Box>
                    </ModalBody>
                </ModalContent>
            </Modal>

            {/* Audit Details Modal */}
            <Modal isOpen={isAuditOpen} onClose={onAuditClose} size="lg">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Bias Audit Details</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        {selectedCandidate && (
                            <Stack spacing={4}>
                                <SimpleGrid columns={2} spacing={4}>
                                    <Card bg="red.50" variant="outline" borderColor="red.200">
                                        <CardBody p={4} textAlign="center">
                                            <Text fontSize="xs" color="red.600" textTransform="uppercase" fontWeight="bold">Status</Text>
                                            <HStack justify="center" mt={2}>
                                                <Icon as={AlertCircle} color="red.500" />
                                                <Text fontWeight="bold" color="red.700">Flagged</Text>
                                            </HStack>
                                        </CardBody>
                                    </Card>
                                    <Card variant="outline">
                                        <CardBody p={4} textAlign="center">
                                            <Text fontSize="xs" color="slate.500" textTransform="uppercase" fontWeight="bold">Fairness Score</Text>
                                            <Heading size="lg" mt={2} color="slate.700">{selectedCandidate.audit.fairness_score}%</Heading>
                                        </CardBody>
                                    </Card>
                                </SimpleGrid>

                                <Box>
                                    <Heading size="sm" mb={3} color="red.700">Detected Flags</Heading>
                                    {selectedCandidate.audit.flags && selectedCandidate.audit.flags.length > 0 ? (
                                        <Stack spacing={2}>
                                            {selectedCandidate.audit.flags.map((flag, idx) => (
                                                <Card key={idx} variant="outline" borderLeftWidth="4px" borderLeftColor="red.400">
                                                    <CardBody py={2} px={4}>
                                                        <HStack>
                                                            <Icon as={AlertCircle} color="red.500" boxSize={4} />
                                                            <Text fontSize="sm" color="slate.700">{flag}</Text>
                                                        </HStack>
                                                    </CardBody>
                                                </Card>
                                            ))}
                                        </Stack>
                                    ) : (
                                        <Text color="slate.500" fontSize="sm">No specific flags provided.</Text>
                                    )}
                                </Box>

                                {selectedCandidate.audit.audit_note && (
                                    <Box>
                                        <Heading size="sm" mb={2} color="slate.700">Auditor Note</Heading>
                                        <Box p={3} bg="slate.50" borderRadius="md" borderWidth="1px" borderColor="slate.200">
                                            <Text fontSize="sm" color="slate.600" whiteSpace="pre-wrap">
                                                {selectedCandidate.audit.audit_note}
                                            </Text>
                                        </Box>
                                    </Box>
                                )}

                                <Box p={3} bg="yellow.50" borderRadius="md" borderWidth="1px" borderColor="yellow.200">
                                    <HStack spacing={2}>
                                        <Icon as={AlertCircle} color="yellow.600" />
                                        <Text fontSize="xs" color="yellow.800" fontWeight="semibold">
                                            This decision has been flagged for human review due to potential bias indicators.
                                        </Text>
                                    </HStack>
                                </Box>
                            </Stack>
                        )}
                    </ModalBody>
                </ModalContent>
            </Modal>

            {/* Delete Confirmation Dialog */}
            <AlertDialog
                isOpen={isDeleteOpen}
                leastDestructiveRef={cancelRef}
                onClose={onDeleteClose}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize="lg" fontWeight="bold">
                            Delete Applicant
                        </AlertDialogHeader>

                        <AlertDialogBody>
                            Are you sure you want to delete this applicant? This action cannot be undone.
                        </AlertDialogBody>

                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={onDeleteClose}>
                                Cancel
                            </Button>
                            <Button colorScheme="red" onClick={handleDelete} ml={3} isLoading={isDeleting}>
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
        </Stack>
    )
}

export default JobDetail
