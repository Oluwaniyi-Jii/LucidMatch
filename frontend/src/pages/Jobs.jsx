import { Box, Heading, Text, SimpleGrid, Card, CardBody, Button, Icon, Stack, Badge, useDisclosure, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, FormControl, FormLabel, Input, Textarea, useToast, VStack } from '@chakra-ui/react'
import { Plus, Briefcase, Users, ArrowRight } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'

const Jobs = () => {
    const [jobs, setJobs] = useState([])
    const { isOpen, onOpen, onClose } = useDisclosure()
    const toast = useToast()

    // Form State
    const [title, setTitle] = useState('')
    const [department, setDepartment] = useState('')
    const [description, setDescription] = useState('')
    const [requirements, setRequirements] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)

    const fetchJobs = async () => {
        try {
            const res = await apiClient.get('/api/jobs')
            setJobs(res.data)
        } catch (error) {
            console.error("Failed to fetch jobs", error)
        }
    }

    useEffect(() => {
        fetchJobs()
    }, [])

    const handleCreateJob = async () => {
        setIsSubmitting(true)
        try {
            await apiClient.post('/api/jobs', {
                title,
                department,
                description,
                requirements
            })
            toast({ title: "Job Created", status: "success" })
            onClose()
            fetchJobs()
            // Reset form
            setTitle('')
            setDepartment('')
            setDescription('')
            setRequirements('')
        } catch (error) {
            toast({ title: "Error creating job", status: "error" })
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Stack spacing={8}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                    <Heading size="lg" mb={2}>Job Listings</Heading>
                    <Text color="slate.500">Manage active roles and track candidate pipelines.</Text>
                </Box>
                <Button leftIcon={<Icon as={Plus} />} colorScheme="brand" onClick={onOpen}>
                    Create Job
                </Button>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {jobs.map((job) => (
                    <Card key={job.id} _hover={{ shadow: 'md', borderColor: 'brand.200' }} transition="all 0.2s">
                        <CardBody>
                            <Stack spacing={4}>
                                <Box display="flex" justifyContent="space-between" alignItems="start">
                                    <Box p={2} bg="brand.50" borderRadius="lg">
                                        <Icon as={Briefcase} color="brand.600" boxSize={5} />
                                    </Box>
                                    <Badge colorScheme={job.department === 'Engineering' ? 'teal' : 'orange'}>
                                        {job.department}
                                    </Badge>
                                </Box>

                                <Box>
                                    <Heading size="md" mb={1}>{job.title}</Heading>
                                    <Text fontSize="sm" color="slate.500" noOfLines={2}>
                                        {job.description}
                                    </Text>
                                </Box>

                                <Button as={Link} to={`/jobs/${job.id}`} variant="outline" rightIcon={<Icon as={ArrowRight} />} w="full" size="sm">
                                    View Candidates
                                </Button>
                            </Stack>
                        </CardBody>
                    </Card>
                ))}
            </SimpleGrid>

            {/* Create Job Modal */}
            <Modal isOpen={isOpen} onClose={onClose} size="xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Create New Job Listing</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <VStack spacing={4}>
                            <FormControl>
                                <FormLabel>Job Title</FormLabel>
                                <Input placeholder="e.g. Senior Product Designer" value={title} onChange={(e) => setTitle(e.target.value)} />
                            </FormControl>
                            <FormControl>
                                <FormLabel>Department</FormLabel>
                                <Input placeholder="e.g. Product" value={department} onChange={(e) => setDepartment(e.target.value)} />
                            </FormControl>
                            <FormControl>
                                <FormLabel>Job Description</FormLabel>
                                <Textarea placeholder="Overview of the role..." value={description} onChange={(e) => setDescription(e.target.value)} />
                            </FormControl>
                            <FormControl>
                                <FormLabel>Requirements</FormLabel>
                                <Textarea h="150px" placeholder="- 5+ years React...&#10;- Experience with..." value={requirements} onChange={(e) => setRequirements(e.target.value)} />
                            </FormControl>
                            <Button colorScheme="brand" w="full" onClick={handleCreateJob} isLoading={isSubmitting}>
                                Create Listing
                            </Button>
                        </VStack>
                    </ModalBody>
                </ModalContent>
            </Modal>
        </Stack>
    )
}

export default Jobs
