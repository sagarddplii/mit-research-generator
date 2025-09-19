import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Download, 
  Copy, 
  ExternalLink, 
  BookOpen,
  Calendar,
  Users,
  TrendingUp,
  Star,
  Hash,
  Eye,
  EyeOff,
  CheckCircle,
  Sparkles,
  Globe,
  FileText,
  ChevronDown,
  ChevronUp,
  Brain,
  FlaskConical,
  PenTool,
  FileDown,
  Package
} from 'lucide-react';

interface Reference {
  id: string;
  number?: number;
  title: string;
  authors: string[];
  journal: string;
  year: string;
  doi?: string;
  url?: string;
  pages?: string;
  volume?: string;
  issue?: string;
  relevance_score: number;
  citations_count: number;
  formatted_citation?: string;
}

interface ReferencesProps {
  references: Reference[];
  citationStyle: 'apa' | 'mla' | 'chicago' | 'ieee';
  onStyleChange?: (style: 'apa' | 'mla' | 'chicago' | 'ieee') => void;
  onReferenceSelect?: (reference: Reference) => void;
  researchData?: any; // Full research data for downloads
}

const References: React.FC<ReferencesProps> = ({
  references,
  citationStyle,
  onStyleChange,
  onReferenceSelect,
  researchData
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'relevance' | 'year' | 'citations' | 'alphabetical'>('relevance');
  const [filterYear, setFilterYear] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [hoveredRef, setHoveredRef] = useState<string | null>(null);
  const [copiedRef, setCopiedRef] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['citations', 'bibliography']));
  const [downloading, setDownloading] = useState<string | null>(null);
  const [showDownloadModal, setShowDownloadModal] = useState(false);

  const filteredAndSortedReferences = useMemo(() => {
    let filtered = references.filter(ref => {
      const matchesSearch = ref.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           ref.authors.some(author => author.toLowerCase().includes(searchTerm.toLowerCase())) ||
                           ref.journal.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesYear = !filterYear || ref.year === filterYear;
      
      return matchesSearch && matchesYear;
    });

    // Sort references
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          return b.relevance_score - a.relevance_score;
        case 'year':
          return parseInt(b.year) - parseInt(a.year);
        case 'citations':
          return b.citations_count - a.citations_count;
        case 'alphabetical':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
  }, [references, searchTerm, sortBy, filterYear]);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const formatCitation = (ref: Reference, style: 'apa' | 'mla' | 'chicago' | 'ieee') => {
    const authors = ref.authors;
    const title = ref.title;
    const journal = ref.journal;
    const year = ref.year;
    const volume = ref.volume;
    const issue = ref.issue;
    const pages = ref.pages;
    const doi = ref.doi;

    switch (style) {
      case 'apa':
        const apaAuthors = authors.length === 1 ? authors[0] :
                          authors.length <= 7 ? authors.slice(0, -1).join(', ') + ', & ' + authors.slice(-1) :
                          authors.slice(0, 6).join(', ') + ', ... ' + authors.slice(-1);
        
        let apaCitation = `${apaAuthors} (${year}). ${title}. `;
        if (journal) {
          apaCitation += journal;
          if (volume) apaCitation += `, ${volume}`;
          if (pages) apaCitation += `, ${pages}`;
        }
        if (doi) apaCitation += ` https://doi.org/${doi}`;
        return apaCitation;

      case 'mla':
        const mlaAuthors = authors.length === 1 ? authors[0] :
                          authors.slice(0, -1).join(', ') + ', and ' + authors.slice(-1);
        
        let mlaCitation = `${mlaAuthors}. "${title}." `;
        if (journal) {
          mlaCitation += journal;
          if (volume) mlaCitation += `, vol. ${volume}`;
          if (pages) mlaCitation += `, ${year}, pp. ${pages}`;
          else mlaCitation += `, ${year}`;
        }
        return mlaCitation;

      case 'chicago':
        const chicagoAuthors = authors.length === 1 ? authors[0] :
                              authors.slice(0, -1).join(', ') + ', and ' + authors.slice(-1);
        
        let chicagoCitation = `${chicagoAuthors}. "${title}." `;
        if (journal) {
          chicagoCitation += journal;
          if (volume) chicagoCitation += ` ${volume}`;
          if (pages) chicagoCitation += `, no. ${issue} (${year}): ${pages}`;
          else chicagoCitation += ` (${year})`;
        }
        if (doi) chicagoCitation += ` https://doi.org/${doi}`;
        return chicagoCitation;

      case 'ieee':
        const ieeeAuthors = authors.length === 1 ? authors[0] :
                           authors.length <= 6 ? authors.join(', ') :
                           authors.slice(0, 3).join(', ') + ' et al.';
        
        let ieeeCitation = `${ieeeAuthors}, "${title}," `;
        if (journal) {
          ieeeCitation += journal;
          if (volume) ieeeCitation += `, vol. ${volume}`;
          if (pages) ieeeCitation += `, pp. ${pages}`;
          ieeeCitation += `, ${year}`;
        }
        return ieeeCitation;

      default:
        return `${authors.join(', ')} (${year}). ${title}. ${journal}`;
    }
  };

  const copyToClipboard = async (text: string, refId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedRef(refId);
      setTimeout(() => setCopiedRef(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const downloadPaper = async (format: string) => {
    if (!researchData) return;
    
    try {
      setDownloading(format);
      
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/download/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          research_data: researchData,
          format: format
        }),
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      // Get the filename from the response headers
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition 
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : `research_paper.${format}`;

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Download error:', error);
      alert(`Download failed: ${error.message}`);
    } finally {
      setDownloading(null);
    }
  };

  const copyAllCitations = async () => {
    const citations = filteredAndSortedReferences.map(ref => formatCitation(ref, citationStyle));
    const text = citations.join('\n\n');
    
    try {
      await navigator.clipboard.writeText(text);
      setCopiedRef('all');
      setTimeout(() => setCopiedRef(null), 2000);
    } catch (err) {
      console.error('Failed to copy citations: ', err);
    }
  };

  const downloadCitations = () => {
    const citations = filteredAndSortedReferences.map(ref => formatCitation(ref, citationStyle));
    const text = citations.join('\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `references_${citationStyle}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getYearRange = () => {
    const years = references.map(ref => parseInt(ref.year)).filter(year => !isNaN(year));
    if (years.length === 0) return [];
    return Array.from({ length: Math.max(...years) - Math.min(...years) + 1 }, (_, i) => Math.min(...years) + i);
  };

  const getCitationStyleColor = (style: string) => {
    const colors: Record<string, string> = {
      'apa': 'from-blue-500 to-blue-600',
      'mla': 'from-green-500 to-green-600',
      'chicago': 'from-purple-500 to-purple-600',
      'ieee': 'from-orange-500 to-orange-600'
    };
    return colors[style] || 'from-gray-500 to-gray-600';
  };

  const getCitationStyleBg = (style: string) => {
    const backgrounds: Record<string, string> = {
      'apa': 'from-blue-50 to-blue-100',
      'mla': 'from-green-50 to-green-100',
      'chicago': 'from-purple-50 to-purple-100',
      'ieee': 'from-orange-50 to-orange-100'
    };
    return backgrounds[style] || 'from-gray-50 to-gray-100';
  };

  const getRelevanceColor = (score: number) => {
    if (score > 0.8) return 'from-green-500 to-emerald-600';
    if (score > 0.6) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  };

  const getAllCitationStyles = () => {
    const styles: Record<string, string[]> = {};
    (['apa', 'mla', 'chicago', 'ieee'] as const).forEach(style => {
      styles[style] = filteredAndSortedReferences.map(ref => formatCitation(ref, style));
    });
    return styles;
  };

  return (
    <motion.div 
      className="max-w-6xl mx-auto bg-white rounded-2xl shadow-2xl border border-gray-200/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Header */}
      <div className="relative bg-gradient-to-br from-green-600 via-blue-600 to-purple-600 text-white overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-r from-green-600/50 via-blue-600/50 to-purple-600/50 animate-pulse"></div>
        
        <div className="relative p-8">
          <div className="flex items-center justify-between mb-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center space-x-3 mb-2">
                <div className="p-3 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl">
                  <BookOpen className="h-6 w-6" />
                </div>
                <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-green-100 bg-clip-text text-transparent">
                  References
                </h2>
              </div>
              <div className="flex items-center space-x-6 text-green-100">
                <div className="flex items-center space-x-2">
                  <Hash className="h-4 w-4" />
                  <span className="font-medium">{filteredAndSortedReferences.length} references found</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-4 w-4" />
                  <span className="font-medium">Multiple citation styles</span>
                </div>
              </div>
            </motion.div>
            
            <motion.div 
              className="flex items-center space-x-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <motion.button
                onClick={copyAllCitations}
                className="flex items-center space-x-2 px-4 py-2 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl transition-all duration-300 border border-white/30"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Copy className="h-4 w-4" />
                <span className="font-medium">Copy All</span>
              </motion.button>
              
              {/* Download Button */}
              <motion.button
                onClick={() => setShowDownloadModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl transition-all duration-300 border border-white/30"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Download className="h-4 w-4" />
                <span className="font-medium">Download</span>
              </motion.button>
            </motion.div>
          </div>

          {/* Citation Style Selector */}
          <motion.div 
            className="flex items-center space-x-4 mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <span className="text-sm font-semibold text-green-100">Citation Style:</span>
            <div className="flex space-x-2">
              {(['apa', 'mla', 'chicago', 'ieee'] as const).map((style) => (
                <motion.button
                  key={style}
                  onClick={() => onStyleChange?.(style)}
                  className={`px-4 py-2 rounded-xl text-sm font-bold transition-all duration-300 ${
                    citationStyle === style
                      ? `bg-gradient-to-r ${getCitationStyleColor(style)} text-white shadow-lg`
                      : 'bg-white/20 text-white hover:bg-white/30'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {style.toUpperCase()}
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Search and Filters */}
          <motion.div 
            className="space-y-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search references..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl focus:ring-4 focus:ring-white/20 focus:border-white placeholder-green-100 font-medium transition-all duration-300"
              />
            </div>

            <div className="flex space-x-4">
              <motion.select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white focus:ring-4 focus:ring-white/20 font-medium transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <option value="relevance" className="text-gray-900">Sort by Relevance</option>
                <option value="year" className="text-gray-900">Sort by Year</option>
                <option value="citations" className="text-gray-900">Sort by Citations</option>
                <option value="alphabetical" className="text-gray-900">Sort Alphabetically</option>
              </motion.select>
              
              <motion.button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white hover:bg-white/30 transition-all duration-300 font-medium"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Filter className="h-4 w-4" />
                <span>Filters</span>
              </motion.button>
            </div>

            {/* Filters */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20"
                >
                  <div className="flex items-center space-x-4">
                    <div>
                      <label className="block text-sm font-semibold text-green-100 mb-2">Year</label>
                      <select
                        value={filterYear}
                        onChange={(e) => setFilterYear(e.target.value)}
                        className="px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:ring-2 focus:ring-white/20 font-medium"
                      >
                        <option value="" className="text-gray-900">All years</option>
                        {getYearRange().reverse().map(year => (
                          <option key={year} value={year.toString()} className="text-gray-900">{year}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>

      <div className="p-8">
        {/* Citation Styles Section */}
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-500" />
            <span>Citation Styles</span>
          </h3>
          
          <div className="space-y-4">
            {Object.entries(getAllCitationStyles()).map(([style, citations], index) => (
              <motion.div 
                key={style} 
                className={`border-2 rounded-2xl overflow-hidden shadow-lg bg-gradient-to-br ${getCitationStyleBg(style)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <motion.button
                  onClick={() => toggleSection(style)}
                  className={`w-full px-6 py-4 text-left rounded-t-2xl flex items-center justify-between bg-gradient-to-r ${getCitationStyleColor(style)} text-white`}
                  whileHover={{ backgroundColor: "rgba(255, 255, 255, 0.1)" }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <FileText className="h-5 w-5" />
                    </div>
                    <span className="font-bold text-lg capitalize">
                      {style} Style ({citations.length} citations)
                    </span>
                  </div>
                  <motion.div
                    animate={{ rotate: expandedSections.has(style) ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChevronUp className="h-5 w-5" />
                  </motion.div>
                </motion.button>
                
                <AnimatePresence>
                  {expandedSections.has(style) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="p-6 space-y-3 max-h-96 overflow-y-auto"
                    >
                      {citations.map((citation, citationIndex) => (
                        <motion.div 
                          key={citationIndex} 
                          className="flex items-start justify-between p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-white/50 shadow-md"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: citationIndex * 0.05 }}
                          whileHover={{ scale: 1.02 }}
                        >
                          <span className="text-sm text-gray-700 flex-1 font-medium leading-relaxed">{citation}</span>
                          <motion.button
                            onClick={() => copyToClipboard(citation, `${style}-${citationIndex}`)}
                            className="ml-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-white/50 rounded-lg transition-all duration-300"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Copy className="h-4 w-4" />
                          </motion.button>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Bibliography Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <motion.button
            onClick={() => toggleSection('bibliography')}
            className="w-full px-6 py-4 text-left bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 rounded-2xl mb-6 flex items-center justify-between border-2 border-green-200 shadow-lg transition-all duration-300"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg">
                <BookOpen className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-green-900 text-lg">
                Bibliography ({filteredAndSortedReferences.length} references)
              </span>
            </div>
            <motion.div
              animate={{ rotate: expandedSections.has('bibliography') ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <ChevronUp className="h-5 w-5 text-green-600" />
            </motion.div>
          </motion.button>

          <AnimatePresence>
            {expandedSections.has('bibliography') && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                {filteredAndSortedReferences.map((ref, index) => (
                  <motion.div
                    key={ref.id}
                    className={`border-2 rounded-2xl p-6 transition-all duration-300 cursor-pointer ${
                      hoveredRef === ref.id 
                        ? 'border-blue-400 shadow-2xl scale-105 bg-gradient-to-br from-blue-50 to-purple-50' 
                        : 'border-gray-200 shadow-lg hover:shadow-xl bg-white'
                    }`}
                    onClick={() => onReferenceSelect?.(ref)}
                    onMouseEnter={() => setHoveredRef(ref.id)}
                    onMouseLeave={() => setHoveredRef(null)}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -5 }}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-3">
                          <span className="text-lg font-bold text-gray-500">[{index + 1}]</span>
                          <motion.div 
                            className={`px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r ${getRelevanceColor(ref.relevance_score)} text-white shadow-md`}
                            whileHover={{ scale: 1.1 }}
                          >
                            {(ref.relevance_score * 100).toFixed(0)}% relevant
                          </motion.div>
                          {ref.citations_count > 0 && (
                            <motion.div 
                              className="px-3 py-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-bold rounded-full shadow-md"
                              whileHover={{ scale: 1.1 }}
                            >
                              {ref.citations_count} citations
                            </motion.div>
                          )}
                        </div>
                        
                        {ref.url ? (
                          <a 
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-bold text-blue-600 hover:text-blue-800 text-lg mb-3 leading-tight block cursor-pointer transition-colors duration-200"
                            onClick={(e) => {
                              e.stopPropagation();
                              console.log('Clicking title link:', ref.url);
                            }}
                          >
                            {ref.title}
                          </a>
                        ) : (
                          <h3 className="font-bold text-gray-900 text-lg mb-3 leading-tight">{ref.title}</h3>
                        )}
                        
                        <div className="text-sm text-gray-600 mb-3 space-y-1">
                          <div className="flex items-center space-x-2">
                            <Users className="h-4 w-4 text-blue-500" />
                            <p className="font-semibold">{ref.authors.join(', ')}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <BookOpen className="h-4 w-4 text-green-500" />
                            <p>{ref.journal} ({ref.year})</p>
                          </div>
                          {(ref.volume || ref.issue || ref.pages) && (
                            <div className="flex items-center space-x-2">
                              <Hash className="h-4 w-4 text-purple-500" />
                              <p>
                                {ref.volume && <span>Volume {ref.volume}</span>}
                                {ref.issue && <span>, Issue {ref.issue}</span>}
                                {ref.pages && <span>, pp. {ref.pages}</span>}
                              </p>
                            </div>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-700 bg-gradient-to-r from-gray-50 to-blue-50 p-4 rounded-xl border-l-4 border-blue-500">
                          <strong className="text-blue-600">{citationStyle.toUpperCase()}:</strong> 
                          <span 
                            dangerouslySetInnerHTML={{
                              __html: formatCitation(ref, citationStyle)
                                .replace(
                                  /(https?:\/\/[^\s]+)/g, 
                                  '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline cursor-pointer font-semibold bg-blue-50 px-1 py-0.5 rounded transition-all duration-200 hover:bg-blue-100">🔗 $1</a>'
                                )
                            }}
                          />
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 ml-4 mt-2">
                        <motion.button
                          onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(formatCitation(ref, citationStyle), ref.id);
                          }}
                          className="flex items-center space-x-1 px-3 py-2 bg-gray-50 text-gray-700 hover:bg-gray-100 hover:text-gray-800 rounded-xl transition-all duration-300 text-sm font-medium border border-gray-200 cursor-pointer shadow-sm hover:shadow-md"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          title="Copy citation to clipboard"
                        >
                          <Copy className="h-4 w-4" />
                          <span>Copy</span>
                        </motion.button>
                        
                        {ref.url && (
                          <motion.a
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => {
                              e.stopPropagation();
                              console.log('Clicking paper link:', ref.url);
                              // Link will open automatically due to href
                            }}
                            className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl transition-all duration-300 text-sm font-bold cursor-pointer shadow-lg hover:shadow-xl transform hover:-translate-y-1 border-2 border-blue-500"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            title="Click to view full paper"
                          >
                            <ExternalLink className="h-4 w-4" />
                            <span>View Paper</span>
                          </motion.a>
                        )}
                        
                        {ref.doi && (
                          <motion.a
                            href={`https://doi.org/${ref.doi}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => {
                              e.stopPropagation();
                              console.log('Clicking DOI link:', `https://doi.org/${ref.doi}`);
                              // Link will open automatically due to href
                            }}
                            className="flex items-center space-x-1 px-3 py-2 bg-purple-50 text-purple-700 hover:bg-purple-100 hover:text-purple-800 rounded-xl transition-all duration-300 text-sm font-medium border border-purple-200 cursor-pointer shadow-sm hover:shadow-md"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            title="Click to view via DOI"
                          >
                            <Globe className="h-4 w-4" />
                            <span>DOI</span>
                          </motion.a>
                        )}
                      </div>
                    </div>

                    {copiedRef === ref.id && (
                      <motion.div 
                        className="mt-3 text-sm text-green-600 font-medium flex items-center space-x-2"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                      >
                        <CheckCircle className="h-4 w-4" />
                        <span>Citation copied to clipboard!</span>
                      </motion.div>
                    )}
                  </motion.div>
                ))}

                {filteredAndSortedReferences.length === 0 && (
                  <motion.div 
                    className="text-center py-12"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No references found</h3>
                    <p className="text-gray-600">
                      {searchTerm || filterYear 
                        ? 'Try adjusting your search or filter criteria.' 
                        : 'No references available for this research session.'}
                    </p>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {copiedRef === 'all' && (
          <motion.div 
            className="mt-6 text-sm text-green-600 font-medium flex items-center justify-center space-x-2 bg-green-50 p-4 rounded-xl"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <CheckCircle className="h-4 w-4" />
            <span>All citations copied to clipboard!</span>
          </motion.div>
        )}
      </div>

      {/* Download Modal */}
      <AnimatePresence>
        {showDownloadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[200]"
            onClick={() => setShowDownloadModal(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-2xl shadow-2xl border border-gray-200 p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center mb-6">
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mx-auto mb-4">
                  <Download className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Download Research Paper</h3>
                <p className="text-gray-600">Choose your preferred format</p>
              </div>

              <div className="space-y-3">
                <motion.button
                  onClick={() => {
                    downloadPaper('txt');
                    setShowDownloadModal(false);
                  }}
                  disabled={downloading === 'txt'}
                  className="w-full flex items-center space-x-4 px-5 py-4 text-left hover:bg-blue-50 hover:border-blue-200 rounded-xl transition-all duration-200 text-gray-800 border-2 border-gray-100 hover:shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FileText className="h-6 w-6 text-gray-600" />
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">Plain Text</div>
                    <div className="text-sm text-gray-600">Universal format (.txt)</div>
                  </div>
                  {downloading === 'txt' && <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
                </motion.button>

                <motion.button
                  onClick={() => {
                    downloadPaper('markdown');
                    setShowDownloadModal(false);
                  }}
                  disabled={downloading === 'markdown'}
                  className="w-full flex items-center space-x-4 px-5 py-4 text-left hover:bg-blue-50 hover:border-blue-200 rounded-xl transition-all duration-200 text-gray-800 border-2 border-gray-100 hover:shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Package className="h-6 w-6 text-blue-600" />
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">Markdown</div>
                    <div className="text-sm text-gray-600">With clickable links (.md)</div>
                  </div>
                  {downloading === 'markdown' && <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
                </motion.button>

                <motion.button
                  onClick={() => {
                    downloadPaper('json');
                    setShowDownloadModal(false);
                  }}
                  disabled={downloading === 'json'}
                  className="w-full flex items-center space-x-4 px-5 py-4 text-left hover:bg-blue-50 hover:border-blue-200 rounded-xl transition-all duration-200 text-gray-800 border-2 border-gray-100 hover:shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Brain className="h-6 w-6 text-green-600" />
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">JSON Data</div>
                    <div className="text-sm text-gray-600">Complete data export (.json)</div>
                  </div>
                  {downloading === 'json' && <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
                </motion.button>

                <motion.button
                  onClick={() => {
                    downloadPaper('bibtex');
                    setShowDownloadModal(false);
                  }}
                  disabled={downloading === 'bibtex'}
                  className="w-full flex items-center space-x-4 px-5 py-4 text-left hover:bg-blue-50 hover:border-blue-200 rounded-xl transition-all duration-200 text-gray-800 border-2 border-gray-100 hover:shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <BookOpen className="h-6 w-6 text-purple-600" />
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">BibTeX References</div>
                    <div className="text-sm text-gray-600">For LaTeX & reference managers (.bib)</div>
                  </div>
                  {downloading === 'bibtex' && <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
                </motion.button>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-200">
                <motion.button
                  onClick={() => setShowDownloadModal(false)}
                  className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default References;