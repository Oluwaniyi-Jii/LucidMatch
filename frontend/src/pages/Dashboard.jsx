import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Button, Icon, Skeleton } from '@chakra-ui/react'
import { Plus, UploadCloud, Users, BarChart3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import apiClient from '../api/client'

const Dashboard = () => {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

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

            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
                <Card>
                    <CardBody>
                        <Stack spacing={4}>
                            <Box p={3} bg="brand.50" w="fit-content" borderRadius="xl">
                                <Icon as={UploadCloud} boxSize={6} color="brand.600" />
                            </Box>
                            <Box>
                                <Text fontWeight="bold" fontSize="lg">New Analysis</Text>
                                <Text fontSize="sm" color="slate.500" mt={1}>Upload a resume to start the AI matching process.</Text>
                            </Box>
                            <Button as={Link} to="/analysis" variant="solid" w="full" leftIcon={<Icon as={Plus} />}>
                                Start Analysis
                            </Button>
                        </Stack>
                    </CardBody>
                </Card>

                {/* Real Stats */}
                <Card>
                    <CardBody>
                        <Stack spacing={2}>
                            <Text fontSize="sm" color="slate.500" fontWeight="medium">Total Candidates</Text>
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
                            <Text fontSize="sm" color="slate.500" fontWeight="medium">Avg Match Score</Text>
                            <Skeleton isLoaded={!loading}>
                                <Heading size="2xl">{stats?.average_score || 0}%</Heading>
                            </Skeleton>
                            <Text fontSize="xs" color="slate.400">Stable</Text>
                        </Stack>
                    </CardBody>
                </Card>
            </SimpleGrid>
        </Stack>
    )
}

export default Dashboard
