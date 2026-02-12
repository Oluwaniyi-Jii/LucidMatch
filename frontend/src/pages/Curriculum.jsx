import { Box, Heading, Text, SimpleGrid, Card, CardBody, Stack, Icon, Badge, Button, Link as ChakraLink } from '@chakra-ui/react'
import { BookOpen, Video, FileText, ExternalLink } from 'lucide-react'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'

const Curriculum = () => {
    const [resources, setResources] = useState([])

    useEffect(() => {
        const fetchResources = async () => {
            try {
                const res = await apiClient.get('/api/curriculum')
                setResources(res.data)
            } catch (error) {
                console.error("Failed to fetch curriculum", error)
            }
        }
        fetchResources()
    }, [])

    const getIcon = (type) => {
        switch (type?.toLowerCase()) {
            case 'course': return Video;
            case 'article': return FileText;
            default: return BookOpen;
        }
    }

    const getColor = (type) => {
        switch (type?.toLowerCase()) {
            case 'course': return 'purple';
            case 'article': return 'blue';
            default: return 'green';
        }
    }

    return (
        <Stack spacing={8}>
            <Box>
                <Heading size="lg" mb={2}>Upskilling Curriculum</Heading>
                <Text color="slate.500">Centralized library of recommended learning resources.</Text>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {resources.map((item, index) => (
                    <Card key={index} _hover={{ shadow: 'md', transform: 'translateY(-2px)' }} transition="all 0.2s">
                        <CardBody>
                            <Stack spacing={4}>
                                <Box display="flex" justifyContent="space-between" alignItems="start">
                                    <Box p={2} bg={`${getColor(item.type)}.50`} borderRadius="lg">
                                        <Icon as={getIcon(item.type)} color={`${getColor(item.type)}.600`} boxSize={5} />
                                    </Box>
                                    <Stack direction="row" spacing={2}>
                                        {item.platform && (
                                            <Badge colorScheme="gray" variant="outline">{item.platform}</Badge>
                                        )}
                                        <Badge colorScheme={getColor(item.type)}>{item.type}</Badge>
                                    </Stack>
                                </Box>

                                <Box>
                                    <Heading size="sm" mb={2}>{item.resource}</Heading>
                                    <Text fontSize="xs" color="slate.500" mb={1}>Target Skill: {item.skill}</Text>
                                    {item.estimated_time && (
                                        <Text fontSize="xs" color="slate.400">{item.estimated_time}</Text>
                                    )}
                                </Box>

                                {item.url ? (
                                    <ChakraLink href={item.url} isExternal _hover={{ textDecoration: 'none' }}>
                                        <Button size="sm" variant="solid" colorScheme="brand" rightIcon={<Icon as={ExternalLink} />} w="full">
                                            Access Resource
                                        </Button>
                                    </ChakraLink>
                                ) : (
                                    <Button size="sm" variant="ghost" rightIcon={<Icon as={ExternalLink} />} justifyContent="flex-start" px={0} isDisabled>
                                        No Link Available
                                    </Button>
                                )}
                            </Stack>
                        </CardBody>
                    </Card>
                ))}

                {resources.length === 0 && (
                    <Box gridColumn={{ md: "span 2", lg: "span 3" }} textAlign="center" py={12} bg="white" borderRadius="xl" borderWidth="1px" borderColor="slate.200">
                        <Icon as={BookOpen} boxSize={10} color="slate.300" mb={4} />
                        <Heading size="md" color="slate.600" mb={2}>Library Empty</Heading>
                        <Text color="slate.500">Run candidate analyses to generate personalized learning paths.</Text>
                    </Box>
                )}
            </SimpleGrid>
        </Stack>
    )
}

export default Curriculum
