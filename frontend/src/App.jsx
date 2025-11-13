/**
 * App.jsx - Main Application Component (Simplified - No Authentication)
 * Direct dashboard access for demo purposes
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/Shared/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import SkincareAnalytics from './components/Skincare/SkincareAnalytics';
import ProductsGrid from './components/Skincare/ProductsGrid';
import 'antd/dist/reset.css';
import './App.css';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          {/* Main dashboard route */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<ProductsGrid />} />
          <Route path="/analytics" element={<SkincareAnalytics />} />

          {/* Default route - 默认显示推荐商品 */}
          <Route path="/" element={<Navigate to="/products" replace />} />

          {/* 404 route */}
          <Route path="*" element={<div><h1>404 - Page Not Found</h1></div>} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
