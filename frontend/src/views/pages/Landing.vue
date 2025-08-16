<script setup lang="ts">
import FeaturesWidget from '@/components/landing/FeaturesWidget.vue';
import FooterWidget from '@/components/landing/FooterWidget.vue';
import HeroWidget from '@/components/landing/HeroWidget.vue';
import HighlightsWidget from '@/components/landing/HighlightsWidget.vue';
import PricingWidget from '@/components/landing/PricingWidget.vue';
import TopbarWidget from '@/components/landing/TopbarWidget.vue';
import { useLoginStore } from '@/store/loginStore';
import { useRouter } from 'vue-router';
if(localStorage.getItem('EZCARE-LOGIN-TOKEN')){
    if(useLoginStore().role === 1){
        useRouter().push({name:'Doctordashboard'})
    }
    else if(useLoginStore().role === 0){
        useRouter().push({name:'Seniordashboard'})
    }
    else if(useLoginStore().role === 2){
        useRouter().push({name: 'ModDashboard'})
    }
}
</script>

<template>
    <div class="bg-surface-0 dark:bg-surface-900">
        <div id="home" class="landing-wrapper overflow-hidden">
            <div class="py-6 px-6 mx-0 md:mx-12 lg:mx-20 lg:px-20 flex items-center justify-between relative lg:static">
                <TopbarWidget />
            </div>
            <HeroWidget />
            <FeaturesWidget />
            <HighlightsWidget />
            <PricingWidget />
            <FooterWidget />
        </div>
    </div>
</template>
