import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'landing',
            component: () => import('@/views/pages/Landing.vue')
        },
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/dashboard',
                    name: 'dashboard',
                    component: () => import('@/views/pages/dashboards/SeniorDashboard.vue')
                },
                {
                    path: '/dashboard2',
                    name: 'Doctordashboard',
                    component: () => import('@/views/pages/dashboards/DoctorDashbaord.vue')
                },
                {
                    path: '/hospital',
                    name: 'hospitalList',
                    component: () => import('@/views/pages/hospital/HospitalList.vue')
                },
                {
                    path: '/doctor',
                    name: 'doctorList',
                    component: () => import('@/views/pages/doctor/DoctorList.vue')
                },
            ]
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            component: () => import('@/views/pages/NotFound.vue'),
        }
    ]
});

export default router;
