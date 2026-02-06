import { Box, Button, Card, CardBody, Center, Heading, Icon, Text, VStack, useToast, Progress, Select, FormControl, FormLabel } from '@chakra-ui/react'
import { UploadCloud, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { useState, useCallback, useEffect } from 'react'
import apiClient from '../api/client'

const FileUpload = ({ onAnalysisComplete }) => {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
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
        setUploadProgress(10)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('job_id', selectedJob)

        try {
            // Mocking progress for UX
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => Math.min(prev + 10, 90))
            }, 500)

            // Connect to real backend endpoint
            const response = await apiClient.post('/api/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            clearInterval(progressInterval)
            setUploadProgress(100)

            toast({
                title: "Analysis Complete",
                description: "The AI has finished processing the resume for this role.",
                status: "success",
                duration: 5000,
                isClosable: true,
            })

            if (onAnalysisComplete) onAnalysisComplete(response.data)

        } catch (error) {
            toast({
                title: "Upload Failed",
                description: error.message,
                status: "error",
                duration: 5000,
                isClosable: true,
            })
            setUploadProgress(0)
        } finally {
            setIsUploading(false)
            setIsDragging(false)
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
                        {isUploading ? (
                            <VStack spacing={4} w="full" maxW="md">
                                <Icon as={FileText} boxSize={12} color="brand.500" className="animate-pulse" />
                                <VStack spacing={1}>
                                    <Heading size="md">Analyzing Resume...</Heading>
                                    <Text color="slate.500" fontSize="sm">This may take a few seconds.</Text>
                                </VStack>
                                <Progress value={uploadProgress} w="full" borderRadius="full" size="sm" colorScheme="brand" />
                            </VStack>
                        ) : (
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
                        )}
                    </Center>
                </CardBody>
            </Card>
        </VStack>
    )
}

export default FileUpload
