import { Box, Button, Card, CardBody, Center, Heading, Icon, Text, VStack, HStack, useToast, Progress, Select, FormControl, FormLabel } from '@chakra-ui/react'
import { keyframes } from '@emotion/react'
import { UploadCloud, FileText, CheckCircle, AlertCircle, Search, Shield, Zap } from 'lucide-react'
import { useState, useCallback, useEffect } from 'react'
import apiClient from '../api/client'

const pulseIcon = keyframes`
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
`

const AGENT_STEPS = [
    { key: 'parser', label: 'Parser Agent', detail: 'Extracting skills & anonymizing PII...', icon: FileText, color: 'teal', duration: 2000 },
    { key: 'reasoner', label: 'Reasoner Agent', detail: 'Scoring 10 evaluation criteria...', icon: Search, color: 'blue', duration: 4000 },
    { key: 'auditor', label: 'Auditor Agent', detail: 'Checking for bias patterns...', icon: Shield, color: 'orange', duration: 2000 },
    { key: 'strategist', label: 'Strategist Agent', detail: 'Building upskilling curriculum...', icon: Zap, color: 'purple', duration: 2000 },
]

const AgentStep = ({ step, status }) => {
    const isActive = status === 'active'
    const isDone = status === 'done'
    const isPending = status === 'pending'

    return (
        <HStack
            spacing={4}
            p={4}
            bg={isDone ? `${step.color}.50` : isActive ? 'white' : 'slate.50'}
            borderWidth="1px"
            borderColor={isDone ? `${step.color}.200` : isActive ? `${step.color}.400` : 'slate.200'}
            transition="all 0.4s ease"
            opacity={isPending ? 0.5 : 1}
        >
            <Box
                p={2}
                bg={isDone ? `${step.color}.100` : isActive ? `${step.color}.50` : 'slate.100'}
                transition="all 0.3s"
            >
                {isDone ? (
                    <Icon as={CheckCircle} boxSize={5} color={`${step.color}.500`} />
                ) : (
                    <Icon
                        as={step.icon}
                        boxSize={5}
                        color={isActive ? `${step.color}.500` : 'slate.400'}
                        animation={isActive ? `${pulseIcon} 1.5s ease-in-out infinite` : 'none'}
                    />
                )}
            </Box>
            <Box flex="1">
                <Text fontWeight="bold" fontSize="sm" color={isPending ? 'slate.400' : 'slate.800'}>
                    {step.label}
                </Text>
                <Text fontSize="xs" color={isActive ? `${step.color}.600` : 'slate.500'}>
                    {isDone ? 'Complete' : isActive ? step.detail : 'Waiting...'}
                </Text>
            </Box>
            {isDone && (
                <Icon as={CheckCircle} boxSize={4} color="green.500" />
            )}
            {isActive && (
                <Progress
                    size="xs"
                    isIndeterminate
                    colorScheme={step.color}
                    w="60px"
                    borderRadius="full"
                />
            )}
        </HStack>
    )
}

const FileUpload = ({ onAnalysisComplete }) => {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [currentStep, setCurrentStep] = useState(-1)
    const [jobs, setJobs] = useState([])
    const [selectedJob, setSelectedJob] = useState('')
    const toast = useToast()

    // Fetch available jobs on mount
    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await apiClient.get('/api/jobs')
                setJobs(res.data)
                if (res.data.length > 0) setSelectedJob(res.data[0].id)
            } catch (error) {
                console.error("Failed to fetch jobs", error)
            }
        }
        fetchJobs()
    }, [])

    const handleDrag = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true)
        } else if (e.type === 'dragleave') {
            setIsDragging(false)
        }
    }, [])

    const processFile = useCallback(async (file) => {
        if (!selectedJob) {
            toast({
                title: "Select a Job",
                description: "Please select which job listing this candidate is applying for.",
                status: "warning"
            })
            return
        }

        setIsUploading(true)
        setCurrentStep(0)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('job_id', selectedJob)

        // Simulate agent step progression during real API call
        const stepInterval = setInterval(() => {
            setCurrentStep(prev => {
                if (prev < AGENT_STEPS.length - 1) return prev + 1
                return prev
            })
        }, 2500)

        try {
            const response = await apiClient.post('/api/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            clearInterval(stepInterval)
            // Show all steps complete
            setCurrentStep(AGENT_STEPS.length)

            // Brief pause to show success state
            await new Promise(resolve => setTimeout(resolve, 800))

            toast({
                title: "Analysis Complete",
                description: "All 4 agents have finished processing the resume.",
                status: "success",
                duration: 5000,
                isClosable: true,
            })

            if (onAnalysisComplete) onAnalysisComplete(response.data)

        } catch (error) {
            clearInterval(stepInterval)
            toast({
                title: "Upload Failed",
                description: error.message,
                status: "error",
                duration: 5000,
                isClosable: true,
            })
        } finally {
            setIsUploading(false)
            setIsDragging(false)
            setCurrentStep(-1)
        }
    }, [selectedJob, toast, onAnalysisComplete])

    const handleDrop = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0])
        }
    }, [processFile])

    const getStepStatus = (index) => {
        if (currentStep >= AGENT_STEPS.length) return 'done' // All complete
        if (index < currentStep) return 'done'
        if (index === currentStep) return 'active'
        return 'pending'
    }

    return (
        <VStack spacing={6} align="stretch">
            <FormControl>
                <FormLabel>Select Role</FormLabel>
                <Select value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)} bg="white">
                    {jobs.map(job => (
                        <option key={job.id} value={job.id}>{job.title} ({job.department})</option>
                    ))}
                    {jobs.length === 0 && <option value="">No Active Jobs (Create one in Job Board)</option>}
                </Select>
            </FormControl>

            <Card borderStyle={isDragging ? 'dashed' : 'solid'} borderColor={isDragging ? 'brand.500' : 'slate.200'} borderWidth="2px">
                <CardBody>
                    {isUploading ? (
                        <VStack spacing={4} py={4}>
                            <VStack spacing={1}>
                                <Heading size="md">Analyzing Resume</Heading>
                                <Text color="slate.500" fontSize="sm">Multi-agent pipeline in progress...</Text>
                            </VStack>

                            <VStack spacing={2} w="full" maxW="lg">
                                {AGENT_STEPS.map((step, index) => (
                                    <AgentStep
                                        key={step.key}
                                        step={step}
                                        status={getStepStatus(index)}
                                    />
                                ))}
                            </VStack>

                            {currentStep >= AGENT_STEPS.length && (
                                <HStack spacing={2} p={3} bg="green.50" borderWidth="1px" borderColor="green.200" w="full" maxW="lg" justify="center">
                                    <Icon as={CheckCircle} color="green.500" />
                                    <Text fontWeight="bold" color="green.700" fontSize="sm">All agents complete — compiling results</Text>
                                </HStack>
                            )}
                        </VStack>
                    ) : (
                        <Center
                            h="300px"
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                            bg={isDragging ? 'brand.50' : 'transparent'}
                            borderRadius="lg"
                            transition="all 0.2s"
                        >
                            <VStack spacing={4}>
                                <Box p={4} bg="slate.50" borderRadius="full">
                                    <Icon as={UploadCloud} boxSize={8} color="brand.500" />
                                </Box>
                                <VStack spacing={1}>
                                    <Heading size="md">Upload Resume</Heading>
                                    <Text color="slate.500">Drag and drop or click to browse</Text>
                                </VStack>
                                <Button variant="outline" onClick={() => document.getElementById('file-input').click()} isDisabled={!selectedJob}>
                                    Select File
                                </Button>
                                <input
                                    type="file"
                                    id="file-input"
                                    style={{ display: 'none' }}
                                    onChange={(e) => e.target.files[0] && processFile(e.target.files[0])}
                                    accept=".pdf,.txt,.docx"
                                />
                                <Text fontSize="xs" color="slate.400">Supported formats: PDF, TXT, DOCX</Text>
                            </VStack>
                        </Center>
                    )}
                </CardBody>
            </Card>
        </VStack>
    )
}

export default FileUpload
