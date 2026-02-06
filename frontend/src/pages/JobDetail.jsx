import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Button, Icon, Table, Thead, Tbody, Tr, Th, Td, Badge, Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton, DrawerHeader, DrawerBody, Progress, HStack, VStack, useDisclosure, Tabs, TabList, TabPanels, Tab, TabPanel, Code, Checkbox, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, Skeleton } from '@chakra-ui/react'
import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'
import SkillRadar from '../components/SkillRadar'
import { AlertCircle, CheckCircle2, BookOpen, Search, Terminal, Activity, Swords } from 'lucide-react'

const JobDetail = () => {
    const { id } = useParams()
    const [job, setJob] = useState(null)
    const [candidates, setCandidates] = useState([])
    const [selectedCandidate, setSelectedCandidate] = useState(null)
    const [compareSelection, setCompareSelection] = useState([])
    const [comparisonData, setComparisonData] = useState(null)
    const [isComparing, setIsComparing] = useState(false)

    // Disclosures
    const { isOpen: isDrawerOpen, onOpen: onDrawerOpen, onClose: onDrawerClose } = useDisclosure()
    const { isOpen: isModalOpen, onOpen: onModalOpen, onClose: onModalClose } = useDisclosure()

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
                        <Text color="slate.500">• {candidates.length} Candidates</Text>
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
                                <Td fontWeight="medium">{c.candidate_name}</Td>
                                <Td isNumeric>
                                    <Badge colorScheme={c.match_score > 75 ? 'green' : c.match_score > 50 ? 'yellow' : 'red'} fontSize="0.9em">
                                        {c.match_score}%
                                    </Badge>
                                </Td>
                                <Td><Badge variant="outline">New</Badge></Td>
                                <Td>
                                    <Button size="sm" variant="ghost" colorScheme="brand" onClick={() => handleViewCandidate(c)}>
                                        Analyze
                                    </Button>
                                </Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Card>

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
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Evidence</Tab>
                                    <Tab _selected={{ bg: 'white', borderBottomColor: 'white', color: 'brand.600', fontWeight: 'bold' }}>Neural Logs</Tab>
                                </TabList>

                                <TabPanels>
                                    {/* 1. OVERVIEW PANEL */}
                                    <TabPanel>
                                        <Stack spacing={6} p={4}>
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

                                    {/* 2. EVIDENCE PANEL */}
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
                                                    <Text key={i} fontSize="sm" color="slate.600">• {adv}</Text>
                                                ))}
                                            </VStack>

                                            <Text fontSize="xs" fontWeight="bold" color="orange.600">CANDIDATE B</Text>
                                            <VStack align="start" spacing={1} pl={2} borderLeft="2px" borderColor="orange.200">
                                                {comparisonData.advantage_b?.map((adv, i) => (
                                                    <Text key={i} fontSize="sm" color="slate.600">• {adv}</Text>
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
        </Stack>
    )
}

export default JobDetail
