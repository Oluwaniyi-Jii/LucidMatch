import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Icon, Table, Thead, Tbody, Tr, Th, Td, Badge, Progress } from '@chakra-ui/react'
import { ShieldCheck, AlertTriangle, CheckCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'

const Governance = () => {
    const [data, setData] = useState(null)

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

    if (!data) return <Text>Loading Governance Data...</Text>

    return (
        <Stack spacing={8}>
            <Box>
                <Heading size="lg" mb={2}>AI Governance</Heading>
                <Text color="slate.500">Monitor system fairness and audit flagged decisions.</Text>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                <Card bg="brand.900" color="white">
                    <CardBody>
                        <Stack spacing={4}>
                            <Box p={3} bg="whiteAlpha.200" w="fit-content" borderRadius="xl">
                                <Icon as={ShieldCheck} boxSize={8} />
                            </Box>
                            <Box>
                                <Text fontSize="sm" opacity={0.8} fontWeight="bold" textTransform="uppercase">System Fairness Score</Text>
                                <Heading size="3xl" mt={2}>{data.fairness_score}%</Heading>
                            </Box>
                            <Progress value={data.fairness_score} size="xs" colorScheme="green" bg="whiteAlpha.300" borderRadius="full" />
                        </Stack>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stack spacing={4}>
                            <Box p={3} bg="orange.50" w="fit-content" borderRadius="xl">
                                <Icon as={AlertTriangle} boxSize={8} color="orange.500" />
                            </Box>
                            <Box>
                                <Text fontSize="sm" color="slate.500" fontWeight="bold" textTransform="uppercase">Flagged Decisions</Text>
                                <Heading size="3xl" mt={2} color="slate.800">{data.flagged_count}</Heading>
                            </Box>
                            <Text fontSize="sm" color="slate.500">Decisions requiring human review due to potential bias.</Text>
                        </Stack>
                    </CardBody>
                </Card>
            </SimpleGrid>

            <Card>
                <CardBody>
                    <Heading size="md" mb={6}>Audit Log</Heading>
                    <Table variant="simple">
                        <Thead bg="slate.50">
                            <Tr>
                                <Th>ID</Th>
                                <Th>Candidate</Th>
                                <Th>Role</Th>
                                <Th>Flags</Th>
                                <Th>Auditor Note</Th>
                                <Th>Status</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {data.flagged_analyses.map((item) => (
                                <Tr key={item.id}>
                                    <Td>#{item.id}</Td>
                                    <Td fontWeight="medium">{item.candidate}</Td>
                                    <Td>{item.role}</Td>
                                    <Td>
                                        <Stack direction="row">
                                            {item.flags.map((flag, i) => (
                                                <Badge key={i} colorScheme="red" variant="subtle">{flag}</Badge>
                                            ))}
                                        </Stack>
                                    </Td>
                                    <Td fontSize="sm" color="slate.600" maxW="300px" isTruncated>{item.note}</Td>
                                    <Td><Badge variant="outline" colorScheme="orange">Review Needed</Badge></Td>
                                </Tr>
                            ))}
                            {data.flagged_analyses.length === 0 && (
                                <Tr>
                                    <Td colSpan={6} textAlign="center" py={8} color="slate.500">
                                        <Stack align="center" spacing={3}>
                                            <Icon as={CheckCircle} boxSize={8} color="green.400" />
                                            <Text>No biased decisions detected. System is healthy.</Text>
                                        </Stack>
                                    </Td>
                                </Tr>
                            )}
                        </Tbody>
                    </Table>
                </CardBody>
            </Card>
        </Stack>
    )
}

export default Governance
