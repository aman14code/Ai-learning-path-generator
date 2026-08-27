import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../api';
import './SkillGraph.css';

/* ============================================================================
   Force-Directed Knowledge Graph — Interactive Course Prerequisite Visualization
   Pure Canvas/JS implementation — no external graph library needed
   ============================================================================ */

function ForceGraph({ nodes, edges, completedCourses, width, height, onNodeClick }) {
  const canvasRef = useRef(null);
  const stateRef = useRef({
    nodes: [],
    edges: [],
    dragging: null,
    hoveredNode: null,
    offsetX: 0,
    offsetY: 0,
    scale: 1,
    panX: 0,
    panY: 0,
    animFrame: null,
    selectedNode: null,
  });

  const initGraph = useCallback(() => {
    if (!nodes.length) return;
    const s = stateRef.current;

    // Initialize node positions in a circular layout by domain
    const domainGroups = {};
    nodes.forEach(n => {
      if (!domainGroups[n.domain]) domainGroups[n.domain] = [];
      domainGroups[n.domain].push(n);
    });

    const domainKeys = Object.keys(domainGroups);
    const cx = width / 2, cy = height / 2;

    s.nodes = nodes.map(n => {
      const domainIdx = domainKeys.indexOf(n.domain);
      const groupNodes = domainGroups[n.domain];
      const idxInGroup = groupNodes.indexOf(n);
      const angle = (domainIdx / domainKeys.length) * 2 * Math.PI;
      const spread = 60 + idxInGroup * 30;
      const jitter = (Math.random() - 0.5) * 40;

      return {
        ...n,
        x: cx + Math.cos(angle) * (120 + spread) + jitter,
        y: cy + Math.sin(angle) * (120 + spread) + jitter,
        vx: 0,
        vy: 0,
        isCompleted: completedCourses.has(n.id),
      };
    });

    s.edges = edges.map(e => ({
      source: s.nodes.find(n => n.id === e.source),
      target: s.nodes.find(n => n.id === e.target),
    })).filter(e => e.source && e.target);

  }, [nodes, edges, completedCourses, width, height]);

  const simulate = useCallback(() => {
    const s = stateRef.current;
    if (!s.nodes.length) return;

    // Force simulation step
    const repulsion = 2500;
    const attraction = 0.008;
    const damping = 0.85;
    const centerForce = 0.002;
    const cx = width / 2, cy = height / 2;

    // Repulsion between all nodes
    for (let i = 0; i < s.nodes.length; i++) {
      for (let j = i + 1; j < s.nodes.length; j++) {
        const a = s.nodes[i], b = s.nodes[j];
        let dx = b.x - a.x, dy = b.y - a.y;
        let dist = Math.sqrt(dx * dx + dy * dy) || 1;
        if (dist < 20) dist = 20;
        const force = repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx -= fx; a.vy -= fy;
        b.vx += fx; b.vy += fy;
      }
    }

    // Attraction along edges
    for (const edge of s.edges) {
      const a = edge.source, b = edge.target;
      const dx = b.x - a.x, dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - 100) * attraction;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      a.vx += fx; a.vy += fy;
      b.vx -= fx; b.vy -= fy;
    }

    // Center gravity
    for (const node of s.nodes) {
      if (s.dragging === node) continue;
      node.vx += (cx - node.x) * centerForce;
      node.vy += (cy - node.y) * centerForce;
      node.x += node.vx;
      node.y += node.vy;
      node.vx *= damping;
      node.vy *= damping;

      // Bounds
      node.x = Math.max(30, Math.min(width - 30, node.x));
      node.y = Math.max(30, Math.min(height - 30, node.y));
    }
  }, [width, height]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const s = stateRef.current;
    const dpr = window.devicePixelRatio || 1;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.translate(s.panX, s.panY);
    ctx.scale(s.scale, s.scale);

    const selectedNode = s.selectedNode;
    const connectedNodes = new Set();
    if (selectedNode) {
      s.edges.forEach(e => {
        if (e.source.id === selectedNode.id) connectedNodes.add(e.target.id);
        if (e.target.id === selectedNode.id) connectedNodes.add(e.source.id);
      });
      connectedNodes.add(selectedNode.id);
    }

    // Draw edges
    for (const edge of s.edges) {
      const isHighlighted = selectedNode && (
        (edge.source.id === selectedNode.id || edge.target.id === selectedNode.id)
      );
      const dimmed = selectedNode && !isHighlighted;

      ctx.beginPath();
      ctx.moveTo(edge.source.x, edge.source.y);
      ctx.lineTo(edge.target.x, edge.target.y);
      ctx.strokeStyle = isHighlighted
        ? 'rgba(99, 102, 241, 0.8)'
        : dimmed ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.1)';
      ctx.lineWidth = isHighlighted ? 2.5 : 1;
      ctx.stroke();

      // Arrow
      if (isHighlighted || !dimmed) {
        const angle = Math.atan2(edge.target.y - edge.source.y, edge.target.x - edge.source.x);
        const arrowSize = isHighlighted ? 8 : 5;
        const midX = (edge.source.x + edge.target.x) / 2;
        const midY = (edge.source.y + edge.target.y) / 2;
        ctx.beginPath();
        ctx.moveTo(midX + arrowSize * Math.cos(angle), midY + arrowSize * Math.sin(angle));
        ctx.lineTo(midX + arrowSize * Math.cos(angle + 2.5), midY + arrowSize * Math.sin(angle + 2.5));
        ctx.lineTo(midX + arrowSize * Math.cos(angle - 2.5), midY + arrowSize * Math.sin(angle - 2.5));
        ctx.closePath();
        ctx.fillStyle = isHighlighted ? 'rgba(99, 102, 241, 0.8)' : 'rgba(255,255,255,0.15)';
        ctx.fill();
      }
    }

    // Draw nodes
    for (const node of s.nodes) {
      const isSelected = selectedNode?.id === node.id;
      const isConnected = connectedNodes.has(node.id);
      const dimmed = selectedNode && !isConnected;
      const isHovered = s.hoveredNode?.id === node.id;
      const r = (node.size || 12) + (isSelected ? 4 : isHovered ? 2 : 0);

      // Glow for completed
      if (node.isCompleted) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, r + 6, 0, Math.PI * 2);
        const glowGrad = ctx.createRadialGradient(node.x, node.y, r, node.x, node.y, r + 8);
        glowGrad.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
        glowGrad.addColorStop(1, 'rgba(16, 185, 129, 0)');
        ctx.fillStyle = glowGrad;
        ctx.fill();
      }

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
      ctx.fillStyle = dimmed
        ? 'rgba(30, 41, 59, 0.5)'
        : node.isCompleted ? '#10b981' : (node.color || '#6366f1');
      ctx.globalAlpha = dimmed ? 0.3 : 1;
      ctx.fill();

      // Border
      ctx.strokeStyle = isSelected
        ? '#fff'
        : isHovered ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.15)';
      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Label
      if (isSelected || isHovered || !dimmed) {
        const label = node.label.length > 22 ? node.label.slice(0, 20) + '…' : node.label;
        ctx.font = `${isSelected || isHovered ? '600 11px' : '500 10px'} Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = dimmed ? 'rgba(148, 163, 184, 0.3)' : 'rgba(241, 245, 249, 0.9)';
        ctx.fillText(label, node.x, node.y + r + 6);
      }
    }

    ctx.restore();

    simulate();
    s.animFrame = requestAnimationFrame(draw);
  }, [width, height, simulate]);

  // Mouse handlers
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const s = stateRef.current;

    function getMousePos(e) {
      const rect = canvas.getBoundingClientRect();
      return {
        x: (e.clientX - rect.left - s.panX) / s.scale,
        y: (e.clientY - rect.top - s.panY) / s.scale,
      };
    }

    function findNode(mx, my) {
      for (const node of s.nodes) {
        const dx = mx - node.x, dy = my - node.y;
        if (dx * dx + dy * dy < (node.size + 5) * (node.size + 5)) return node;
      }
      return null;
    }

    function onMouseDown(e) {
      const pos = getMousePos(e);
      const node = findNode(pos.x, pos.y);
      if (node) {
        s.dragging = node;
        s.offsetX = pos.x - node.x;
        s.offsetY = pos.y - node.y;
      }
    }

    function onMouseMove(e) {
      const pos = getMousePos(e);
      if (s.dragging) {
        s.dragging.x = pos.x - s.offsetX;
        s.dragging.y = pos.y - s.offsetY;
        s.dragging.vx = 0;
        s.dragging.vy = 0;
      }
      const node = findNode(pos.x, pos.y);
      s.hoveredNode = node;
      canvas.style.cursor = node ? 'pointer' : 'default';
    }

    function onMouseUp() {
      s.dragging = null;
    }

    function onClick(e) {
      const pos = getMousePos(e);
      const node = findNode(pos.x, pos.y);
      s.selectedNode = node;
      if (node && onNodeClick) onNodeClick(node);
    }

    function onWheel(e) {
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 0.95 : 1.05;
      s.scale = Math.max(0.3, Math.min(3, s.scale * zoomFactor));
    }

    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('click', onClick);
    canvas.addEventListener('wheel', onWheel, { passive: false });

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('click', onClick);
      canvas.removeEventListener('wheel', onWheel);
    };
  }, [onNodeClick]);

  // Init + animate
  useEffect(() => {
    initGraph();
    const s = stateRef.current;
    s.animFrame = requestAnimationFrame(draw);
    return () => {
      if (s.animFrame) cancelAnimationFrame(s.animFrame);
    };
  }, [initGraph, draw]);

  return <canvas ref={canvasRef} className="force-graph-canvas" />;
}

/* ============================================================================
   SkillGraph Page Component
   ============================================================================ */

export default function SkillGraph({ user }) {
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterDomain, setFilterDomain] = useState('');
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 900, height: 600 });

  useEffect(() => {
    loadGraph();
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  function updateDimensions() {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({
        width: Math.max(600, rect.width - 40),
        height: Math.max(450, window.innerHeight - 340),
      });
    }
  }

  async function loadGraph() {
    setLoading(true);
    try {
      const data = await api.getGraph();
      setGraphData(data);
    } catch (err) {
      console.error('Failed to load graph:', err);
    }
    setLoading(false);
  }

  const completedSet = new Set(user?.completed_courses || []);

  // Filter nodes by domain
  const filteredNodes = graphData?.nodes?.filter(n =>
    !filterDomain || n.domain === filterDomain
  ) || [];
  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = graphData?.edges?.filter(e =>
    filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target)
  ) || [];

  return (
    <div className="skill-graph-page animate-fade-in">
      <div className="page-header">
        <h2>Knowledge Graph</h2>
        <p>Interactive visualization of course prerequisites and learning paths. Click nodes to explore, drag to rearrange, scroll to zoom.</p>
      </div>

      {/* Domain Filter */}
      <div className="graph-controls">
        <div className="domain-filters">
          <button
            className={`domain-filter-btn ${!filterDomain ? 'active' : ''}`}
            onClick={() => setFilterDomain('')}
          >
            All Domains
          </button>
          {(graphData?.domains || []).map(d => (
            <button
              key={d}
              className={`domain-filter-btn ${filterDomain === d ? 'active' : ''}`}
              onClick={() => setFilterDomain(filterDomain === d ? '' : d)}
              style={{
                '--domain-color': graphData?.domain_colors?.[d] || '#6366f1',
              }}
            >
              <span
                className="domain-color-dot"
                style={{ background: graphData?.domain_colors?.[d] }}
              />
              {d}
            </button>
          ))}
        </div>
        <div className="graph-stats-bar">
          <span>{filteredNodes.length} courses</span>
          <span>•</span>
          <span>{filteredEdges.length} prerequisites</span>
          <span>•</span>
          <span className="completed-count">{completedSet.size} completed</span>
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="graph-container premium-3d-card" ref={containerRef}>
        {loading ? (
          <div className="graph-loading">
            <div className="spinner" style={{ width: 40, height: 40 }} />
            <p>Building knowledge graph...</p>
          </div>
        ) : (
          <ForceGraph
            nodes={filteredNodes}
            edges={filteredEdges}
            completedCourses={completedSet}
            width={dimensions.width}
            height={dimensions.height}
            onNodeClick={setSelectedNode}
          />
        )}
      </div>

      {/* Selected Node Detail */}
      {selectedNode && (
        <div className="node-detail glass-card animate-scale-in">
          <div className="node-detail-header">
            <div>
              <h3>{selectedNode.label}</h3>
              <div className="node-detail-meta">
                <span
                  className="domain-badge"
                  style={{ background: selectedNode.color + '22', color: selectedNode.color }}
                >
                  {selectedNode.domain}
                </span>
                <span className={`badge badge-${selectedNode.difficulty === 1 ? 'beginner' : selectedNode.difficulty === 2 ? 'intermediate' : 'advanced'}`}>
                  {selectedNode.difficulty === 1 ? 'Beginner' : selectedNode.difficulty === 2 ? 'Intermediate' : 'Advanced'}
                </span>
                <span className="node-duration">{selectedNode.duration_hours}h</span>
                {completedSet.has(selectedNode.id) && (
                  <span className="node-completed-badge">✓ Completed</span>
                )}
              </div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => setSelectedNode(null)}>✕</button>
          </div>
          <p className="node-description">{selectedNode.description}</p>
          {selectedNode.skills?.length > 0 && (
            <div className="node-skills">
              <strong>Skills:</strong>
              <div className="node-skill-tags">
                {selectedNode.skills.map(s => <span key={s} className="tag">{s}</span>)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="graph-legend">
        <div className="legend-section">
          <span className="legend-title">Node Size</span>
          <span className="legend-desc">= Difficulty Level</span>
        </div>
        <div className="legend-section">
          <span className="legend-title">Node Color</span>
          <span className="legend-desc">= Domain</span>
        </div>
        <div className="legend-section">
          <span className="legend-dot" style={{ background: '#10b981', boxShadow: '0 0 8px rgba(16,185,129,0.5)' }} />
          <span className="legend-desc">= Completed</span>
        </div>
        <div className="legend-section">
          <span className="legend-title">Arrows</span>
          <span className="legend-desc">= Prerequisites</span>
        </div>
      </div>
    </div>
  );
}
