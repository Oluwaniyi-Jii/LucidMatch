import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Button, Icon, Skeleton, HStack, Badge, VStack, Divider, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react'
import { Plus, UploadCloud, Briefcase, AlertTriangle, ShieldCheck, FileText, TrendingUp, Eye } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import apiClient from '../api/client'

const Dashboard = () => {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await apiClient.get('/api/stats')
                setStats(response.data)
            } catch (error) {
                console.error("Failed to fetch stats", error)
            } finally {
                setLoading(false)
            }
        }
        fetchStats()
    }, [])

    return (
        <Stack spacing={8}>
            <Box>
                <Heading size="lg" mb={2}>Welcome back</Heading>
                <Text color="slate.500">Here's what's happening with your recruitment pipeline.</Text>
            </Box>

            {/* Main Stats Grid */}
            <SimpleGrid columns={{ base: 1, md: 2, lg: 5 }} spacing={6}>
                <Card>
                    <CardBody>
                        <Stack spacing={2}>
                            <HStack spacing={2}>
                                <Icon as={FileText} boxSize={4} color="slate.400" />
                                <Text fontSize="sm" color="slate.500" fontWeight="medium">Total Candidates</Text>
                            </HStack>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl">{stats?.total_candidates || 0}</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color="brand.600" fontWeight="bold">{stats?.trend || "No data yet"}</Text>
                        </Stack>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stack spacing={2}>
                            <HStack spacing={2}>
                                <Icon as={Briefcase} boxSize={4} color="slate.400" />
                                <Text fontSize="sm" color="slate.500" fontWeight="medium">Active Jobs</Text>
                            </HStack>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl">{stats?.active_jobs || 0}</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color="slate.400">Open positions</Text>
                        </Stack>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <Stack spacing={2}>
                            <HStack spacing={2}>
                                <Icon as={TrendingUp} boxSize={4} color="slate.400" />
                                <Text fontSize="sm" color="slate.500" fontWeight="medium">Avg Match Score</Text>
                            </HStack>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl">{stats?.average_score || 0}%</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color="slate.400">Across all candidates</Text>
                        </Stack>
                    </CardBody>
                </Card>

                <Card bg={stats?.flagged_count > 0 ? "orange.50" : "white"} borderColor={stats?.flagged_count > 0 ? "orange.200" : "slate.200"}>
                    <CardBody>
                        <Stack spacing={2}>
                            <HStack spacing={2}>
                                <Icon as={AlertTriangle} boxSize={4} color={stats?.flagged_count > 0 ? "orange.500" : "slate.400"} />
                                <Text fontSize="sm" color={stats?.flagged_count > 0 ? "orange.700" : "slate.500"} fontWeight="medium">Flagged for Review</Text>
                            </HStack>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl" color={stats?.flagged_count > 0 ? "orange.600" : "slate.800"}>{stats?.flagged_count || 0}</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color={stats?.flagged_count > 0 ? "orange.600" : "slate.400"}>Bias concerns detected</Text>
                        </Stack>
                    </CardBody>
                </Card>

                <Card bg="brand.900" color="white">
                    <CardBody>
                        <Stack spacing={2}>
                            <HStack spacing={2}>
                                <Icon as={ShieldCheck} boxSize={4} color="whiteAlpha.800" />
                                <Text fontSize="sm" color="whiteAlpha.800" fontWeight="medium">System Fairness</Text>
                            </HStack>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl">{stats?.avg_fairness || 100}%</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color="whiteAlpha.700">AI governance score</Text>
                        </Stack>
                    </CardBody>
                </Card>
            </SimpleGrid>

            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                {/* Recent Analyses */}
                <Card>
                    <CardBody>
                        <HStack justify="space-between" mb={4}>
                            <Heading size="sm">Recent Analyses</Heading>
                            <Button as={Link} to="/jobs" size="xs" variant="ghost">View All</Button>
                        </HStack>
                        {loading ? (
                            <Stack spacing={3}>
                                {[1, 2, 3].map(i => <Skeleton key={i} height="50px" />)}
                            </Stack>
                        ) : stats?.recent_analyses?.length > 0 ? (
                            <VStack spacing={3} align="stretch">
                                {stats.recent_analyses.map((item) => (
                                    <Box
                                        key={item.id}
                                        p={3}
                                        bg="slate.50"
                                        borderRadius="md"
                                        cursor="pointer"
                                        _hover={{ bg: "brand.50" }}
                                        onClick={() => navigate(`/jobs/${item.job_id}`)}
                                    >
                                        <HStack justify="space-between">
                                            <VStack align="start" spacing={0}>
                                                <Text fontWeight="bold" fontSize="sm">{item.candidate}</Text>
                                                <Text fontSize="xs" color="slate.500">{item.role}</Text>
                                            </VStack>
                                            <Badge colorScheme={item.score >= 70 ? "green" : item.score >= 50 ? "orange" : "red"}>
                                                {item.score}%
                                            </Badge>
                                        </HStack>
                                    </Box>
                                ))}
                            </VStack>
                        ) : (
                            <Box textAlign="center" py={8}>
                                <Text color="slate.400" fontSize="sm">No analyses yet</Text>
                            </Box>
                        )}
                    </CardBody>
                </Card>

                {/* Top Candidates */}
                <Card>
                    <CardBody>
                        <HStack justify="space-between" mb={4}>
                            <Heading size="sm">Top Candidates</Heading>
                            <Button as={Link} to="/jobs" size="xs" variant="ghost">View All</Button>
                        </HStack>
                        {loading ? (
                            <Stack spacing={3}>
                                {[1, 2, 3].map(i => <Skeleton key={i} height="50px" />)}
                            </Stack>
                        ) : stats?.top_candidates?.length > 0 ? (
                            <VStack spacing={3} align="stretch">
                                {stats.top_candidates.map((item, idx) => (
                                    <Box
                                        key={item.id}
                                        p={3}
                                        bg="slate.50"
                                        borderRadius="md"
                                        cursor="pointer"
                                        _hover={{ bg: "brand.50" }}
                                        onClick={() => navigate(`/jobs/${item.job_id}`)}
                                    >
                                        <HStack justify="space-between">
                                            <HStack spacing={3}>
                                                <Badge colorScheme="brand" variant="solid" fontSize="xs">#{idx + 1}</Badge>
                                                <VStack align="start" spacing={0}>
                                                    <Text fontWeight="bold" fontSize="sm">{item.candidate}</Text>
                                                    <Text fontSize="xs" color="slate.500">{item.role}</Text>
                                                </VStack>
                                            </HStack>
                                            <Badge colorScheme="green" fontSize="md">
                                                {item.score}%
                                            </Badge>
                                        </HStack>
                                    </Box>
                                ))}
                            </VStack>
                        ) : (
                            <Box textAlign="center" py={8}>
                                <Text color="slate.400" fontSize="sm">No candidates yet</Text>
                            </Box>
                        )}
                    </CardBody>
                </Card>
            </SimpleGrid>

            {/* Quick Actions */}
            <Card>
                <CardBody>
                    <Heading size="sm" mb={4}>Quick Actions</Heading>
                    <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
                        <Button as={Link} to="/analysis" leftIcon={<Icon as={UploadCloud} />} colorScheme="brand" size="lg">
                            Upload Resume
                        </Button>
                        <Button as={Link} to="/jobs" leftIcon={<Icon as={Plus} />} variant="outline" size="lg">
                            Create Job
                        </Button>
                        <Button as={Link} to="/governance" leftIcon={<Icon as={Eye} />} variant="outline" size="lg">
                            View Governance
                        </Button>
                        <Button as={Link} to="/upskill" leftIcon={<Icon as={TrendingUp} />} variant="outline" size="lg">
                            Upskill Plans
                        </Button>
                    </SimpleGrid>
                </CardBody>
            </Card>
        </Stack>
    )
}

export default Dashboard
