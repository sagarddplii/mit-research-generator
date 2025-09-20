import React, { useState } from 'react';
import { Search, FileText, BarChart3, BookOpen, Loader2, Sparkles, Brain, TrendingUp, ArrowRight, FileEdit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SearchBar from '../components/SearchBar';
import SummaryCard from '../components/SummaryCard';
import PaperDraft from '../components/PaperDraft';
import References from '../components/References';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

interface SearchFilters {
  maxPapers: number;
  sources: string[];
  dateRange: {
    start: string;
    end: string;
  };
  paperType: string;
}

interface ResearchData {
  topic: string;
  papers: any[];
  summaries: any;
  citations: any;
  draft_paper: any;
  references: any[];
  analytics: any;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  processing_time?: number;
}

const Home: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<'search' | 'results' | 'paper' | 'analytics'>('search');
  const [researchData, setResearchData] = useState<ResearchData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'papers' | 'summaries' | 'draft' | 'references' | 'analytics'>('papers');
  // const [selectedReference, setSelectedReference] = useState<any>(null);

  const handleSearch = async (query: string, filters: SearchFilters) => {
    if (loading) {
      console.log('Search already in progress, ignoring duplicate request');
      return;
    }
    
    setLoading(true);
    setError(null);
    setCurrentStep('results');

    try {
      // Connect to the backend API using environment variable
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'http://localhost:8000';
      console.log('Using API Base URL:', apiBaseUrl);
      console.log('Environment vars:', import.meta.env);
      
      // Add timeout to prevent infinite loading
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('Request timeout after 60 seconds');
        controller.abort();
      }, 60000); // 60 second timeout (backend takes ~4 seconds)
      console.log('Making API call to:', `${apiBaseUrl}/research-pipeline`);
      console.log('Request payload:', {
        query: query,
        max_papers: filters.maxPapers,
        sources: filters.sources,
        paper_length: filters.paperType === 'short' ? 'short' : filters.paperType === 'long' ? 'long' : 'medium',
        citation_style: 'apa'
      });
      
      const response = await fetch(`${apiBaseUrl}/research-pipeline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          max_papers: filters.maxPapers,
          sources: filters.sources,
          paper_length: filters.paperType === 'short' ? 'short' : filters.paperType === 'long' ? 'long' : 'medium',
          citation_style: 'apa'
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        throw new Error('Failed to generate research paper');
      }

      const data = await response.json();
      console.log('Backend response:', data); // Debug logging
      
      if (data.status === 'error') {
        throw new Error(data.error || 'Pipeline execution failed');
      }
      
      // Normalize backend response to frontend shape
      const normalized = {
        topic: data.query,
        papers: data.papers || [],
        summaries: data.summaries || {},
        citations: data.citations || {},
        draft_paper: data.draft_paper || data.draft || null,
        references: data.references || data.papers || [], // Use proper references field
        analytics: data.analytics || null,
        status: data.status || 'completed',
        processing_time: data.processing_time
      } as ResearchData;
      
      console.log('Normalized data:', normalized); // Debug logging
      setResearchData(normalized);
      setCurrentStep('results');
      setActiveTab('papers');
    } catch (err: any) {
      console.error('API call failed:', err);
      console.error('Error details:', {
        name: err.name,
        message: err.message,
        stack: err.stack
      });
      
      if (err.name === 'AbortError') {
        console.log('Request was aborted - checking if it was timeout or other reason');
        setError('Request was interrupted. The backend might be processing your request. Please try again.');
        return;
      }
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Network error: Cannot connect to backend. Please check if the backend is running.');
        return;
      }
      
      // Fallback: create mock data so the app remains usable without backend
      const now = new Date().toISOString();
      const mockPapers = [
        {
          id: 'p1',
          title: `${query} - A Comprehensive Overview`,
          authors: ['Alice Smith', 'Bob Johnson'],
          abstract: `This paper explores ${query} with a focus on recent advancements and applications.`,
          published_date: '2023-06-01',
          journal: 'Journal of Research',
          url: 'https://example.com/paper1',
          relevance_score: 0.85,
          citations_count: 42,
          year: 2023
        }
      ];
      const mockSummaries = {
        thematic_summary: `Key themes in ${query} include methodology, applications, and future directions.`,
        key_findings: [
          { finding: `Significant progress in ${query} since 2020`, papers: mockPapers, confidence: 0.8 }
        ],
        methodology_summary: { experimental: mockPapers, computational: mockPapers },
        individual_summaries: [
          { paper_id: 'p1', title: mockPapers[0].title, summary: mockPapers[0].abstract, key_points: [], relevance_score: 0.85 }
        ],
        gaps_and_opportunities: ['Need for larger datasets', 'Standardized benchmarks']
      } as any;
      const mockDraft = {
        title: `${query}: A Mock Generated Paper`,
        abstract: `This mock abstract summarizes ${query} and references findings [1].`,
        sections: {
          introduction: `Introduction to ${query}.`,
          literature_review: `A review of ${query} literature.`,
          discussion: `Discussion on ${query}.`,
          conclusion: `Conclusions about ${query}.`
        },
        metadata: { topic: query, word_count: 1200, generation_date: now }
      };
      const mockReferences = [
        {
          id: 'r1',
          title: `${query} Study`,
          authors: ['Alice Smith', 'Bob Johnson'],
          journal: 'Journal of Research',
          year: '2023',
          relevance_score: 0.9,
          citations_count: 42,
          url: 'https://example.com/paper1'
        }
      ];
      const mockAnalytics = {
        paper_metrics: {
          word_count: 1200,
          section_count: 4,
          abstract_length: 25,
          average_section_length: 300,
          readability_score: 0.6,
          citation_density: 12
        },
        content_analysis: {
          keywords: [query.split(' ')[0] || 'topic', 'analysis', 'methodology'],
          topics: ['Applications', 'Trends'],
          sentiment: { positive: 0.6, negative: 0.1, neutral: 0.3 },
          coherence_score: 0.8,
          academic_tone_score: 0.7
        },
        source_analysis: {
          total_sources: 1,
          publication_years: { earliest: 2023, latest: 2023, average: 2023, median: 2023 },
          journal_diversity: 1,
          author_diversity: 2,
          citation_impact: { total_citations: 42, average_citations: 42, median_citations: 42, max_citations: 42 },
          relevance_analysis: { average_relevance: 0.85, median_relevance: 0.85, high_relevance_count: 1 }
        },
        trend_analysis: {
          publication_trends: { year_distribution: { '2023': 1 }, growth_rate: 0.0, recent_activity: 1 },
          methodological_trends: { experimental: 1, computational: 1 },
          topic_trends: { [query.split(' ')[0] || 'topic']: 1 }
        },
        recommendations: ['Increase citation density', 'Add methodology details']
      } as any;

      const normalized = {
        topic: query,
        papers: mockPapers as any[],
        summaries: mockSummaries,
        citations: {},
        draft_paper: mockDraft,
        references: mockReferences as any[],
        analytics: mockAnalytics,
        status: 'completed'
      } as ResearchData;

      setResearchData(normalized);
      setCurrentStep('paper');
    } finally {
      setLoading(false);
    }
  };

  // const handleStepChange = (step: 'search' | 'results' | 'paper' | 'analytics') => {
  //   setCurrentStep(step);
  // };

  const handleReferenceSelect = (_reference: any) => {
    // Selection can be handled as needed
  };

  const renderStepIndicator = () => {
    const steps = [
      { id: 'search', label: 'Search', icon: <Search className="h-4 w-4" /> },
      { id: 'results', label: 'Analysis', icon: <Brain className="h-4 w-4" /> },
      { id: 'paper', label: 'Generate', icon: <FileText className="h-4 w-4" /> },
      { id: 'analytics', label: 'Insights', icon: <BarChart3 className="h-4 w-4" /> }
    ];

    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-6xl mx-auto mb-12"
      >
        <div className="relative overflow-hidden rounded-3xl p-8 shadow-2xl">
          {/* Apple-style water effect background */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-400/30 via-purple-500/20 to-pink-400/30 backdrop-blur-3xl"></div>
          <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent animate-pulse"></div>
          <div className="absolute inset-0 opacity-40">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-radial from-blue-400/40 to-transparent rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-gradient-radial from-purple-500/30 to-transparent rounded-full blur-3xl animate-pulse delay-1000"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-radial from-pink-400/20 to-transparent rounded-full blur-2xl animate-pulse delay-500"></div>
          </div>
          <div className="relative flex items-center justify-between z-10">
          
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <motion.div 
                className="flex items-center space-x-3 relative z-10"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <motion.div 
                  className={`flex items-center justify-center w-10 h-10 rounded-full border-2 shadow-lg ${
                    currentStep === step.id || (researchData && currentStep !== 'search')
                      ? 'border-gradient-to-r from-blue-500 to-purple-600 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-blue-500/25'
                      : 'border-gray-300 bg-white text-gray-500 hover:border-gray-400'
                  }`}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: "spring", stiffness: 400, damping: 17 }}
                >
                  {loading && currentStep === step.id ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    step.icon
                  )}
                </motion.div>
                <span className={`text-sm font-semibold ${
                  currentStep === step.id || (researchData && currentStep !== 'search')
                    ? 'text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600'
                    : 'text-gray-500'
                }`}>
                  {step.label}
                </span>
              </motion.div>
              {index < steps.length - 1 && (
                <div className="flex-1 mx-6" />
              )}
            </React.Fragment>
          ))}
        </div>
        </div>
      </motion.div>
    );
  };

  const renderSearchStep = () => (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="space-y-12"
    >
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-6 shadow-2xl shadow-blue-500/25">
          <Sparkles className="h-10 w-10 text-white" />
        </div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
          MIT Research Paper Generator
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Generate comprehensive research papers with AI-powered analysis, 
          automatic citation management, and quality assessment. Transform your research ideas into 
          <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> publication-ready papers</span> in minutes.
        </p>
      </motion.div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <SearchBar onSearch={handleSearch} loading={loading} />
      </motion.div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl p-6 shadow-lg">
              <div className="flex">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="h-6 w-6 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-red-800">Generation Error</h3>
                  <div className="mt-2 text-red-700">
                    {error}
                  </div>
                  <button 
                    onClick={() => setError(null)}
                    className="mt-3 text-sm text-red-600 hover:text-red-800 font-medium"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Features */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-4">
            Powerful Features
          </h2>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Everything you need to transform research ideas into publication-ready papers
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: <Search className="h-8 w-8" />,
              title: "Smart Search",
              description: "Search across multiple academic databases including arXiv, PubMed, and Google Scholar to find the most relevant papers.",
              gradient: "from-blue-500 to-cyan-500",
              bgGradient: "from-blue-50 to-cyan-50"
            },
            {
              icon: <Brain className="h-8 w-8" />,
              title: "AI-Powered Analysis",
              description: "Advanced AI algorithms analyze papers, extract key findings, and generate comprehensive summaries.",
              gradient: "from-green-500 to-emerald-500",
              bgGradient: "from-green-50 to-emerald-50"
            },
            {
              icon: <FileText className="h-8 w-8" />,
              title: "Paper Generation",
              description: "Generate well-structured research papers with proper citations, methodology, and academic formatting.",
              gradient: "from-purple-500 to-violet-500",
              bgGradient: "from-purple-50 to-violet-50"
            },
            {
              icon: <BarChart3 className="h-8 w-8" />,
              title: "Quality Analytics",
              description: "Comprehensive analytics and quality assessment to ensure your paper meets academic standards.",
              gradient: "from-orange-500 to-red-500",
              bgGradient: "from-orange-50 to-red-50"
            },
            {
              icon: <BookOpen className="h-8 w-8" />,
              title: "Citation Management",
              description: "Automatic citation formatting in multiple styles (APA, MLA, Chicago, IEEE) with proper reference management.",
              gradient: "from-pink-500 to-rose-500",
              bgGradient: "from-pink-50 to-rose-50"
            },
            {
              icon: <TrendingUp className="h-8 w-8" />,
              title: "Trend Analysis",
              description: "Analyze research trends, identify gaps, and discover emerging topics in your field of study.",
              gradient: "from-indigo-500 to-blue-500",
              bgGradient: "from-indigo-50 to-blue-50"
            }
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
              className="group relative"
            >
              <div className={`bg-gradient-to-br ${feature.bgGradient} p-8 rounded-2xl shadow-lg border border-white/20 hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2`}>
                <div className="flex items-center space-x-4 mb-6">
                  <div className={`p-3 bg-gradient-to-r ${feature.gradient} rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <div className="text-white">
                      {feature.icon}
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-gray-900 group-hover:to-gray-600 transition-all duration-300">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
                <div className="mt-6 flex items-center text-sm font-medium text-gray-500 group-hover:text-gray-700 transition-colors duration-300">
                  <span>Learn more</span>
                  <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );

  const renderTabbedInterface = () => {
    if (!researchData) return null;

    const tabs = [
      { id: 'papers', label: 'Papers', icon: <FileText className="h-4 w-4" />, count: researchData.papers?.length || 0 },
      { id: 'summaries', label: 'Summaries', icon: <Brain className="h-4 w-4" />, count: Object.keys(researchData.summaries || {}).length },
      { id: 'draft', label: 'Draft', icon: <FileEdit className="h-4 w-4" />, count: researchData.draft_paper ? 1 : 0 },
      { id: 'references', label: 'References', icon: <BookOpen className="h-4 w-4" />, count: researchData.references?.length || 0 },
      { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-4 w-4" />, count: researchData.analytics ? 1 : 0 }
    ];

    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-6"
      >
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Research Results for "{researchData.topic}"
          </h2>
          <p className="text-gray-600">
            Pipeline completed in {researchData.processing_time?.toFixed(2)}s • Found {researchData.papers?.length || 0} papers
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center">
          <div className="bg-gray-100 p-1 rounded-lg inline-flex space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.count > 0 && (
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    activeTab === tab.id 
                      ? 'bg-blue-100 text-blue-600' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[600px]">
          {activeTab === 'papers' && renderPapersTab()}
          {activeTab === 'summaries' && renderSummariesTab()}
          {activeTab === 'draft' && renderDraftTab()}
          {activeTab === 'references' && renderReferencesTab()}
          {activeTab === 'analytics' && renderAnalyticsTab()}
        </div>
      </motion.div>
    );
  };

  const renderPapersTab = () => {
    if (!researchData?.papers) return null;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Retrieved Papers</h3>
        <div className="grid gap-4">
          {researchData.papers.map((paper, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-lg font-semibold text-gray-900 line-clamp-2">{paper.title}</h4>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full ml-2">
                  {paper.source}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                <span>{paper.authors?.join(', ') || 'Unknown authors'}</span>
                <span>•</span>
                <span>{paper.year}</span>
                <span>•</span>
                <span>{paper.citation_count} citations</span>
                <span>•</span>
                <span>Relevance: {(paper.relevance_score * 100).toFixed(1)}%</span>
              </div>
              
              <p className="text-gray-700 text-sm leading-relaxed mb-4 line-clamp-3">
                {paper.abstract || 'No abstract available'}
              </p>
              
              <div className="flex justify-between items-center">
                <div className="flex space-x-2">
                  {paper.doi && (
                    <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer"
                       className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      View DOI
                    </a>
                  )}
                  {paper.url && (
                    <a href={paper.url} target="_blank" rel="noopener noreferrer"
                       className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      View Paper
                    </a>
                  )}
                </div>
                <span className="text-xs text-gray-500">#{index + 1}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    );
  };

  const renderSummariesTab = () => {
    if (!researchData?.summaries) return null;

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Summaries</h3>
        {Object.entries(researchData.summaries).map(([key, summary]: [string, any]) => (
          <SummaryCard
            key={key}
            summary={{
              type: key as any,
              title: key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
              content: summary,
              metadata: {
                paper_count: researchData.papers?.length || 0,
                average_relevance: researchData.papers?.reduce((acc: number, p: any) => acc + (p.relevance_score || 0), 0) / (researchData.papers?.length || 1) || 0
              }
            }}
            onPaperSelect={handleReferenceSelect}
          />
        ))}
      </div>
    );
  };

  const renderDraftTab = () => {
    if (!researchData?.draft_paper) return null;

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Paper Draft</h3>
        <PaperDraft 
          paper={researchData.draft_paper}
          references={researchData.references}
          editable={true}
        />
      </div>
    );
  };

  const renderReferencesTab = () => {
    if (!researchData?.references || researchData.references.length === 0) {
      return (
        <div className="text-center py-12">
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md mx-auto">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No References Available</h3>
            <p className="text-gray-600">
              References will appear here once papers are analyzed.
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">References & Citations</h3>
        <References
          references={researchData.references}
          citationStyle="apa"
          onReferenceSelect={handleReferenceSelect}
          researchData={researchData}
        />
      </div>
    );
  };

  const renderAnalyticsTab = () => {
    if (!researchData?.analytics) return null;

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Analytics</h3>
        <AnalyticsDashboard 
          analytics={researchData.analytics}
          papers={researchData.papers}
        />
      </div>
    );
  };

  const renderPaperStep = () => {
    if (!researchData?.draft_paper) return null;

    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-8"
      >
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Generated Paper
            </h2>
            <p className="text-gray-600 mt-2">Your AI-generated research paper is ready</p>
          </div>
          <div className="flex space-x-3">
            <motion.button
              onClick={() => setCurrentStep('analytics')}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>View Analytics</span>
              </div>
            </motion.button>
            <motion.button
              onClick={() => setCurrentStep('results')}
              className="px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center space-x-2">
                <Brain className="h-4 w-4" />
                <span>Back to Analysis</span>
              </div>
            </motion.button>
          </div>
        </div>

        {renderTabbedInterface()}
      </motion.div>
    );
  };

  const renderAnalyticsStep = () => {
    if (!researchData?.analytics) {
      return (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center py-12"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md mx-auto">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Available</h3>
            <p className="text-gray-600 mb-4">
              Analytics data is not available for this research session.
            </p>
            <button
              onClick={() => setCurrentStep('paper')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Paper
            </button>
          </div>
        </motion.div>
      );
    }

    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-8"
      >
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Analytics Dashboard
            </h2>
            <p className="text-gray-600 mt-2">Comprehensive insights into your research</p>
          </div>
          <div className="flex space-x-3">
            <motion.button
              onClick={() => setCurrentStep('paper')}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Back to Paper</span>
              </div>
            </motion.button>
          </div>
        </div>

        <AnalyticsDashboard analytics={researchData.analytics} />
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      <div className="container mx-auto px-4 py-8">
        {renderStepIndicator()}
        
        <AnimatePresence mode="wait">
          {currentStep === 'search' && (
            <motion.div
              key="search"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.5 }}
            >
              {renderSearchStep()}
            </motion.div>
          )}
          {currentStep === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.5 }}
            >
              {renderTabbedInterface()}
            </motion.div>
          )}
          {currentStep === 'paper' && (
            <motion.div
              key="paper"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.5 }}
            >
              {renderPaperStep()}
            </motion.div>
          )}
          {currentStep === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.5 }}
            >
              {renderAnalyticsStep()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Home;
