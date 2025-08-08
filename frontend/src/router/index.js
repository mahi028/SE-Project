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
                    name: 'Seniordashboard',
                    component: () => import('@/views/pages/dashboards/SeniorDashboard.vue'),
                    meta: { roles: [0] },
                },
                {
                    path: '/dashboard2',
                    name: 'Doctordashboard',
                    component: () => import('@/views/pages/dashboards/DoctorDashbaord.vue'),
                    meta: { roles: [1] },
                },
                {
                    path: '/mod-dashboard',
                    name: 'ModDashboard',
                    component: () => import('@/views/pages/dashboards/ModDashboard.vue'),
                    meta: { roles: [2] },
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
                {
                    path: '/doctor/:ez_id',
                    name: 'DoctorProfile',
                    component: () => import('@/views/pages/profile/DoctorProfile.vue')
                },
                {
                    path: '/senior/:ez_id',
                    name: 'SeniorProfile',
                    component: () => import('@/views/pages/profile/SeniorProfile.vue')
                },
                {
                    path: 'doctor/registration',
                    name: 'DoctorRegistration',
                    component: () => import('@/views/pages/auth/DoctorRegistration.vue'),
                    meta: { roles: [1] },
                },
                {
                    path: 'senior/registration',
                    name: 'SeniorRegistration',
                    component: () => import('@/views/pages/auth/SeniorRegistration.vue'),
                    meta: { roles: [0] },
                }
            ]
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/auth/access',
            name: 'access',
            component: () => import('@/views/pages/auth/Access.vue')
        },
        {
            path: '/auth/register',
            name: 'register',
            component: () => import('@/views/pages/auth/Register.vue')
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            component: () => import('@/views/pages/NotFound.vue'),
        }
    ]
});

export default router;
