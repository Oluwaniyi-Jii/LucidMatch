import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Icon, Badge, Progress, HStack, VStack, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Input, InputGroup, InputLeftElement, Stat, StatLabel, StatNumber, StatHelpText } from '@chakra-ui/react'
import { keyframes } from '@emotion/react'
import { ShieldCheck, AlertTriangle, CheckCircle, Search, FileText, Eye, Zap, ArrowRight, Shield, User } from 'lucide-react'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'

const flowPulse = keyframes`
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
`

const nodeGlow = keyframes`
    0%, 100% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0); }
    50% { box-shadow: 0 0 12px 2px rgba(20, 184, 166, 0.15); }
`

const FlowNode = ({ icon, label, sublabel, color = 'brand', isHighlight = false }) => (
    <VStack spacing={1} flex="1" minW="90px">
        <Box
            p={3}
            bg={isHighlight ? `${color}.100` : `${color}.50`}
            borderWidth="2px"
            borderColor={isHighlight ? `${color}.400` : `${color}.200`}
            animation={isHighlight ? `${nodeGlow} 2s ease-in-out infinite` : 'none'}
        >
            <Icon as={icon} boxSize={5} color={`${color}.500`} />
        </Box>
        <Text fontSize="xs" fontWeight="bold" color="slate.700" textAlign="center">{label}</Text>
        {sublabel && (
            <Text fontSize="10px" color="slate.400" textAlign="center" lineHeight="1.2">{sublabel}</Text>
        )}
    </VStack>
)

const FlowArrow = ({ label }) => (
    <VStack spacing={0} flex="0 0 auto" justify="center" pb="30px">
        <Box position="relative" display="flex" alignItems="center">
            <Box
                w="32px"
                h="2px"
                bgGradient="linear(to-r, slate.200, slate.400)"
                backgroundSize="200% 100%"
                animation={`${flowPulse} 2s linear infinite`}
            />
            <Icon as={ArrowRight} boxSize={3} color="slate.400" ml={-1} />
        </Box>
        {label && (
            <Text fontSize="8px" color="slate.400" fontWeight="bold" textTransform="uppercase" mt={0.5}>
                {label}
            </Text>
        )}
    </VStack>
)

const FlowBranch = ({ flaggedCount }) => (
    <VStack spacing={0} position="relative" mt={1} align="center">
        <Box w="2px" h="12px" bg="orange.300" />
        <Box
            px={3}
            py={1.5}
            bg={flaggedCount > 0 ? "orange.100" : "slate.50"}
            borderWidth="1px"
            borderColor={flaggedCount > 0 ? "orange.400" : "slate.200"}
            borderStyle={flaggedCount > 0 ? "solid" : "dashed"}
            whiteSpace="nowrap"
        >
            <Text fontSize="10px" fontWeight="bold" color={flaggedCount > 0 ? "orange.700" : "slate.500"} textAlign="center">
                🚩 Flagged → Human Review
            </Text>
            <Text fontSize="9px" color={flaggedCount > 0 ? "orange.600" : "slate.400"} textAlign="center">
                {flaggedCount > 0 ? `${flaggedCount} flagged` : 'None'}
            </Text>
        </Box>
    </VStack>
)

const Governance = () => {
    const [data, setData] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await apiClient.get('/api/governance')
                setData(res.data)
            } catch (error) {
                console.error("Failed to fetch governance data", error)
            }
        }
        fetchData()
    }, [])

    const filteredAnalyses = data?.flagged_analyses?.filter(item =>
        item.id?.toString().includes(searchTerm) ||
        item.candidate?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.flags?.some(f => f.toLowerCase().includes(searchTerm.toLowerCase()))
    ) || []

    if (!data) return (
        <Stack spacing={8}>
            <Box>
                <Heading size="lg" mb={2}>AI Governance</Heading>
                <Text color="slate.500">Loading governance data...</Text>
            </Box>
        </Stack>
    )

    return (
        <Stack spacing={8}>
            <Box>
                <Heading size="lg" mb={2}>AI Governance & Transparency</Heading>
                <Text color="slate.500">Monitor system fairness, audit decisions, and understand the AI decision-making process.</Text>
            </Box>

            {/* Decision Flow Visualization */}
            <Card>
                <CardBody>
                    <HStack justify="space-between" mb={4}>
                        <Box>
                            <Heading size="sm">Decision Flow</Heading>
                            <Text fontSize="xs" color="slate.400">How every candidate is processed — no black boxes</Text>
                        </Box>
                        <Badge colorScheme="brand" variant="subtle">LIVE PIPELINE</Badge>
                    </HStack>

                    <Box
                        bg="slate.50"
                        p={6}
                        pb={16}
                        borderWidth="1px"
                        borderColor="slate.200"
                        position="relative"
                    >
                        {/* Main pipeline row */}
                        <HStack spacing={0} justify="center" align="end" flexWrap="nowrap" minW="600px">
                            <FlowNode icon={User} label="Resume" sublabel="Upload" color="slate" />
                            <FlowArrow />
                            <FlowNode icon={Shield} label="Anonymize" sublabel="Strip PII" color="slate" />
                            <FlowArrow />
                            <FlowNode icon={FileText} label="Parser" sublabel="Extract Skills" color="teal" isHighlight />
                            <FlowArrow />
                            <FlowNode icon={Eye} label="Reasoner" sublabel="10 Criteria" color="blue" isHighlight />
                            <FlowArrow />

                            {/* Auditor node with branch */}
                            <Box position="relative">
                                <FlowNode icon={AlertTriangle} label="Auditor" sublabel="Bias Check" color="orange" isHighlight={data.flagged_count > 0} />
                                <Box position="absolute" top="100%" left="50%" transform="translateX(-50%)" zIndex={1}>
                                    <FlowBranch flaggedCount={data.flagged_count} />
                                </Box>
                            </Box>

                            <FlowArrow />
                            <FlowNode icon={Zap} label="Strategist" sublabel="Upskilling" color="purple" isHighlight />
                            <FlowArrow />
                            <FlowNode icon={CheckCircle} label="Decision" sublabel="Glass Box" color="green" />
                        </HStack>
                    </Box>

                    {/* Pipeline stats */}
                    <SimpleGrid columns={3} spacing={4} mt={4}>
                        <Box p={3} bg="green.50" borderWidth="1px" borderColor="green.200" textAlign="center">
                            <Text fontSize="xs" fontWeight="bold" color="green.600" textTransform="uppercase">Analyzed</Text>
                            <Text fontSize="xl" fontWeight="bold" color="green.700">{data.total_analyzed}</Text>
                        </Box>
                        <Box p={3} bg="orange.50" borderWidth="1px" borderColor="orange.200" textAlign="center">
                            <Text fontSize="xs" fontWeight="bold" color="orange.600" textTransform="uppercase">Flagged</Text>
                            <Text fontSize="xl" fontWeight="bold" color="orange.700">{data.flagged_count}</Text>
                        </Box>
                        <Box p={3} bg="brand.50" borderWidth="1px" borderColor="brand.200" textAlign="center">
                            <Text fontSize="xs" fontWeight="bold" color="brand.600" textTransform="uppercase">Audit Rate</Text>
                            <Text fontSize="xl" fontWeight="bold" color="brand.700">100%</Text>
                        </Box>
                    </SimpleGrid>
                </CardBody>
            </Card>

            {/* Stats Overview */}
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                <Card bg="brand.900" color="white">
                    <CardBody>
                        <Stat>
                            <StatLabel opacity={0.8} fontWeight="bold" textTransform="uppercase" fontSize="xs">System Fairness</StatLabel>
                            <StatNumber fontSize="4xl">{data.fairness_score}%</StatNumber>
                            <Progress value={data.fairness_score} size="xs" colorScheme="green" bg="whiteAlpha.300" borderRadius="full" mt={2} />
                        </Stat>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stat>
                            <HStack mb={2}>
                                <Box p={2} bg="orange.50" borderRadius="lg">
                                    <Icon as={AlertTriangle} boxSize={5} color="orange.500" />
                                </Box>
                            </HStack>
                            <StatLabel color="slate.500" fontWeight="bold" textTransform="uppercase" fontSize="xs">Flagged Decisions</StatLabel>
                            <StatNumber color="slate.800">{data.flagged_count}</StatNumber>
                            <StatHelpText color="slate.400">Require human review</StatHelpText>
                        </Stat>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stat>
                            <HStack mb={2}>
                                <Box p={2} bg="green.50" borderRadius="lg">
                                    <Icon as={CheckCircle} boxSize={5} color="green.500" />
                                </Box>
                            </HStack>
                            <StatLabel color="slate.500" fontWeight="bold" textTransform="uppercase" fontSize="xs">Bias Detection Rate</StatLabel>
                            <StatNumber color="slate.800">
                                {data.total_analyzed > 0 ? Math.round((data.flagged_count / data.total_analyzed) * 100) : 0}%
                            </StatNumber>
                            <StatHelpText color="slate.400">Of all analyzed candidates</StatHelpText>
                        </Stat>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stat>
                            <HStack mb={2}>
                                <Box p={2} bg="teal.50" borderRadius="lg">
                                    <Icon as={ShieldCheck} boxSize={5} color="teal.500" />
                                </Box>
                            </HStack>
                            <StatLabel color="slate.500" fontWeight="bold" textTransform="uppercase" fontSize="xs">Audit Coverage</StatLabel>
                            <StatNumber color="slate.800">100%</StatNumber>
                            <StatHelpText color="slate.400">All decisions audited</StatHelpText>
                        </Stat>
                    </CardBody>
                </Card>
            </SimpleGrid>

            {/* Audit Log */}
            <Card>
                <CardBody>
                    <HStack justify="space-between" mb={6}>
                        <Heading size="md">Audit Log</Heading>
                        <InputGroup maxW="300px">
                            <InputLeftElement>
                                <Icon as={Search} color="slate.400" />
                            </InputLeftElement>
                            <Input
                                placeholder="Search candidates, roles, flags..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </InputGroup>
                    </HStack>

                    {filteredAnalyses.length > 0 ? (
                        <Accordion allowMultiple>
                            {filteredAnalyses.map((item) => (
                                <AccordionItem key={item.id} border="1px" borderColor="slate.200" borderRadius="lg" mb={3}>
                                    <AccordionButton py={4} _expanded={{ bg: 'brand.50' }}>
                                        <HStack flex={1} justify="space-between">
                                            <HStack spacing={4}>
                                                <Badge colorScheme="orange" variant="solid">#{item.id}</Badge>
                                                <Box textAlign="left">
                                                    <Text fontWeight="bold">{item.candidate}</Text>
                                                    <Text fontSize="sm" color="slate.500">{item.role}</Text>
                                                </Box>
                                            </HStack>
                                            <HStack>
                                                {item.flags?.slice(0, 2).map((flag, i) => (
                                                    <Badge key={i} colorScheme="red" variant="subtle">{flag}</Badge>
                                                ))}
                                                {item.flags?.length > 2 && (
                                                    <Badge colorScheme="gray">+{item.flags.length - 2}</Badge>
                                                )}
                                            </HStack>
                                        </HStack>
                                        <AccordionIcon ml={4} />
                                    </AccordionButton>
                                    <AccordionPanel pb={4} bg="slate.50">
                                        <VStack align="stretch" spacing={4}>
                                            <Box>
                                                <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={2}>ALL FLAGS</Text>
                                                <HStack wrap="wrap" spacing={2}>
                                                    {item.flags?.map((flag, i) => (
                                                        <Badge key={i} colorScheme="red" variant="subtle" fontSize="sm">{flag}</Badge>
                                                    ))}
                                                </HStack>
                                            </Box>
                                            <Box>
                                                <Text fontSize="xs" fontWeight="bold" color="slate.500" mb={2}>AUDITOR NOTE</Text>
                                                <Text fontSize="sm" color="slate.700" bg="white" p={3} borderRadius="md">
                                                    {item.note || "No additional notes from auditor."}
                                                </Text>
                                            </Box>
                                            <Box>
                                                <Badge variant="outline" colorScheme="orange">Review Needed</Badge>
                                            </Box>
                                        </VStack>
                                    </AccordionPanel>
                                </AccordionItem>
                            ))}
                        </Accordion>
                    ) : (
                        <Box textAlign="center" py={12}>
                            <Icon as={CheckCircle} boxSize={12} color="green.400" mb={4} />
                            <Heading size="md" color="slate.600" mb={2}>
                                {searchTerm ? 'No Matching Results' : 'System Healthy'}
                            </Heading>
                            <Text color="slate.500">
                                {searchTerm
                                    ? 'Try adjusting your search terms.'
                                    : 'No biased decisions detected. All evaluations are within acceptable fairness thresholds.'
                                }
                            </Text>
                        </Box>
                    )}
                </CardBody>
            </Card>
        </Stack>
    )
}

export default Governance
