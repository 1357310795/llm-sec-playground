import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import CourseHomePage from './routes/CourseHomePage';
import ReplayPage from './routes/ReplayPage';
import ScenarioDetailPage from './routes/ScenarioDetailPage';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<CourseHomePage />} />
        <Route path="/scenarios/:scenarioId" element={<ScenarioDetailPage />} />
        <Route path="/attempts/:attemptId/replay" element={<ReplayPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
