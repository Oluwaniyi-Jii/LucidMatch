/**
 * LucidMatch API Service
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

// API Base URL - change this if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8080';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Check API health status
 */
export const getHealthStatus = async () => {
    const response = await api.get('/');
    return response.data;
};

/**
 * Get all available jobs
 */
export const getJobs = async () => {
    const response = await api.get('/api/jobs');
    return response.data;
};

/**
 * Get a specific job by ID
 */
export const getJob = async (jobId) => {
    const response = await api.get(`/api/jobs/${jobId}`);
    return response.data;
};

/**
 * Analyze a resume (parse only)
 */
export const analyzeResume = async (resumeText, anonymize = true) => {
    const response = await api.post('/api/analyze', {
        resume_text: resumeText,
        anonymize: anonymize,
    });
    return response.data;
};

/**
 * Full analysis pipeline: Parse -> Match -> Upskill -> Audit
 */
export const fullAnalysis = async (resumeText, jobIds = null, includeUpskilling = true, includeAudit = true) => {
    const response = await api.post('/api/analyze/full', {
        resume_text: resumeText,
        job_ids: jobIds,
        include_upskilling: includeUpskilling,
        include_audit: includeAudit,
    });
    return response.data;
};

/**
 * Match a parsed profile against jobs
 */
export const matchProfile = async (profile, jobIds = null) => {
    const response = await api.post('/api/match', {
        profile: profile,
        job_ids: jobIds,
    });
    return response.data;
};

/**
 * Get upskilling recommendations
 */
export const getUpskilling = async (matchResult) => {
    const response = await api.post('/api/upskill', {
        match_result: matchResult,
    });
    return response.data;
};

/**
 * Audit a match decision
 */
export const auditDecision = async (matchResult, profile = null) => {
    const response = await api.post('/api/audit', {
        match_result: matchResult,
        profile: profile,
    });
    return response.data;
};

/**
 * Quick demo match
 */
export const quickMatch = async (resumeText, jobId) => {
    const formData = new FormData();
    formData.append('resume_text', resumeText);
    formData.append('job_id', jobId);
    
    const response = await api.post('/api/demo/quick-match', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

/**
 * Batch analysis for multiple resumes (Phase 3)
 */
export const batchAnalysis = async (resumes, jobIds = null, includeUpskilling = true, includeAudit = true) => {
    const response = await api.post('/api/analyze/batch', {
        resumes: resumes,
        job_ids: jobIds,
        include_upskilling: includeUpskilling,
        include_audit: includeAudit,
    });
    return response.data;
};

/**
 * Get cost estimate for processing
 */
export const getCostEstimate = async (profileCount = 1) => {
    const response = await api.get(`/api/cost/estimate?profile_count=${profileCount}`);
    return response.data;
};

export default api;
