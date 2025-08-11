<script setup>
import { useLayout } from '@/layout/composables/layout';
import AppConfigurator from './AppConfigurator.vue';
import { useLoginStore } from '@/store/loginStore';
import { useRouter } from 'vue-router';
const { toggleDarkMode, isDarkTheme } = useLayout();
const loginStore = useLoginStore()
const router = useRouter()
const logout = async () => {
    loginStore.clearLoginDetails();
    router.push('/')
}
const roleBasedDashboardName = (role) => {
    switch (role){
        case 0:
            return "Seniordashboard";
        case 1:
            return "Doctordashboard";
        case 2:
            return "ModDashboard";
    }
};
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <!-- <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button> -->

            <router-link v-if="loginStore.ezId == null" :to="{name: 'landing'}" class="layout-topbar-logo">
                <img src="/images/logo-transparent.png" alt="EZCare Logo" class="h-12 mr-2" />
                <span>EZCare</span>
            </router-link>
            <router-link v-else :to="{name: roleBasedDashboardName(loginStore.role)}" class="layout-topbar-logo">
                <img src="/images/logo-transparent.png" alt="EZCare Logo" class="h-12 mr-2" />
                <span>EZCare</span>
            </router-link>
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                </button>
                <div class="relative">
                    <button
                        v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
                        type="button"
                        class="layout-topbar-action layout-topbar-action-highlight"
                    >
                        <i class="pi pi-palette"></i>
                    </button>
                    <AppConfigurator />
                </div>
            </div>

            <button
                class="layout-topbar-menu-button layout-topbar-action"
                v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
            >
                <i class="pi pi-ellipsis-v"></i>
            </button>

            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
                    <!--  -->
                    <RouterLink v-if="['senior','doctor'].includes(loginStore.role)" :to="`/${loginStore.role}/${loginStore.ez_id}`" class="layout-topbar-action">
                        <i class="pi pi-user"></i>
                        <span>Profile</span>
                    </RouterLink>
                    <Button v-if="loginStore.ezId" @click="logout()" label="Logout" severity="danger" rounded />
                </div>
            </div>
        </div>
    </div>
</template>
