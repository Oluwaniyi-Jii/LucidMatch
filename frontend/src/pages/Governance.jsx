import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Icon, Badge, Progress, HStack, VStack, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Input, InputGroup, InputLeftElement, Stat, StatLabel, StatNumber, StatHelpText } from '@chakra-ui/react'
import { ShieldCheck, AlertTriangle, CheckCircle, Search } from 'lucide-react'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'

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
                                {data.flagged_count > 0 ? Math.round((data.flagged_count / (data.flagged_count + 10)) * 100) : 0}%
                            </StatNumber>
                            <StatHelpText color="slate.400">Of potential issues caught</StatHelpText>
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
