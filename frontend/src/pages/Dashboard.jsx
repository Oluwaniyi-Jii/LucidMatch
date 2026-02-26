import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Button, Icon, Skeleton, HStack, Badge, VStack, Divider } from '@chakra-ui/react'
import { keyframes } from '@emotion/react'
import { Plus, UploadCloud, Briefcase, AlertTriangle, ShieldCheck, FileText, TrendingUp, Eye, ArrowRight, Zap, Search as SearchIcon, Shield } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import apiClient from '../api/client'

const pulseGlow = keyframes`
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
`

const flowPulse = keyframes`
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
`

const AgentNode = ({ icon, label, color, delay }) => (
    <VStack spacing={2} flex="1" position="relative">
        <Box
            p={4}
            bg={`${color}.50`}
            border="1px solid"
            borderColor={`${color}.200`}
            animation={`${pulseGlow} 3s ease-in-out ${delay}s infinite`}
        >
            <Icon as={icon} boxSize={6} color={`${color}.500`} />
        </Box>
        <Text fontSize="xs" fontWeight="bold" color="slate.600" textTransform="uppercase" letterSpacing="wider">
            {label}
        </Text>
    </VStack>
)

const FlowArrow = () => (
    <Box flex="0 0 auto" display="flex" alignItems="center" pb="22px">
        <Box
            w="40px"
            h="2px"
            bgGradient="linear(to-r, brand.200, brand.400)"
            backgroundSize="200% 100%"
            animation={`${flowPulse} 2s linear infinite`}
        />
        <Icon as={ArrowRight} boxSize={4} color="brand.400" ml={-1} />
    </Box>
)

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
            {/* Hero Section */}
            <Box
                bg="brand.900"
                color="white"
                p={10}
                position="relative"
                overflow="hidden"
                border="1px solid"
                borderColor="slate.900"
            >
                {/* Decorative grid */}
                <Box
                    position="absolute"
                    top={0} left={0} right={0} bottom={0}
                    opacity={0.05}
                    backgroundImage="linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)"
                    backgroundSize="40px 40px"
                />

                <VStack spacing={6} position="relative" zIndex={1}>
                    <VStack spacing={3} textAlign="center">
                        <Badge
                            bg="whiteAlpha.200"
                            color="brand.200"
                            px={3} py={1}
                            fontSize="xs"
                            fontWeight="bold"
                            textTransform="uppercase"
                            letterSpacing="widest"
                        >
                            Glass Box AI for Talent
                        </Badge>
                        <Heading size="xl" letterSpacing="tight">
                            Where AI Meets Accountability
                        </Heading>
                        <Text color="whiteAlpha.800" maxW="2xl" fontSize="md" lineHeight="tall">
                            Prism uses a multi-agent pipeline to match candidates beyond keywords — with full
                            explainability, bias detection, and personalized upskilling for every decision.
                        </Text>
                    </VStack>


                    <HStack spacing={4} pt={2}>
                        <Button
                            as={Link}
                            to="/analysis"
                            bg="white"
                            color="brand.900"
                            size="lg"
                            leftIcon={<Icon as={UploadCloud} />}
                            _hover={{ bg: 'brand.50', transform: 'translateY(-2px)' }}
                            transition="all 0.2s"
                            borderColor="white"
                        >
                            Analyze a Resume
                        </Button>
                        <Button
                            as={Link}
                            to="/governance"
                            variant="outline"
                            size="lg"
                            color="white"
                            borderColor="whiteAlpha.400"
                            leftIcon={<Icon as={ShieldCheck} />}
                            _hover={{ bg: 'whiteAlpha.100', borderColor: 'whiteAlpha.600' }}
                        >
                            View Governance
                        </Button>
                    </HStack>
                </VStack>
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

                <Card bg={stats?.flagged_count > 0 ? "orange.50" : "white"} borderColor={stats?.flagged_count > 0 ? "orange.900" : "slate.900"} borderWidth="1px">
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
                                        borderRadius="0"
                                        borderWidth="1px"
                                        borderColor="slate.900"
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
                                        borderRadius="0"
                                        borderWidth="1px"
                                        borderColor="slate.900"
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
