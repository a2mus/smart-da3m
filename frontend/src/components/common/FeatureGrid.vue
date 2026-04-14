<script setup lang="ts">
// T008 [US1] FeatureGrid component
</script>

<template>
  <section class="bg-surface-container-low py-24 px-6">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-16">
        <h2 class="text-4xl font-bold text-primary mb-4">لماذا يختار الأولياء إحسان؟</h2>
        <p class="text-on-surface-variant max-w-2xl mx-auto">نحن نجمع بين الخبرة البيداغوجية الجزائرية وأحدث تقنيات التعليم الرقمي</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Feature 1 -->
        <div class="bg-surface-container-lowest p-10 rounded-3xl shadow-sm hover:shadow-md transition-shadow group">
          <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 text-primary group-hover:bg-primary group-hover:text-white transition-all">
            <span class="material-symbols-outlined text-4xl" data-icon="psychology">psychology</span>
          </div>
          <h3 class="text-2xl font-bold text-primary mb-4">التعلم التكيفي</h3>
          <p class="text-on-surface-variant leading-relaxed">تتغير صعوبة الأسئلة والمحتوى تلقائياً بناءً على مستوى فهم طفلك لضمان عدم الملل أو الإحباط.</p>
        </div>
        <!-- Feature 2 -->
        <div class="bg-surface-container-lowest p-10 rounded-3xl shadow-sm hover:shadow-md transition-shadow group">
          <div class="w-16 h-16 bg-secondary/10 rounded-2xl flex items-center justify-center mb-6 text-secondary group-hover:bg-secondary group-hover:text-white transition-all">
            <span class="material-symbols-outlined text-4xl" data-icon="family_history">family_history</span>
          </div>
          <h3 class="text-2xl font-bold text-primary mb-4">متابعة دقيقة للأولياء</h3>
          <p class="text-on-surface-variant leading-relaxed">تقارير دورية وشاملة تصلك مباشرة، توضح نقاط القوة والمجالات التي تحتاج إلى تحسين في أداء طفلك.</p>
        </div>
        <!-- Feature 3 -->
        <div class="bg-surface-container-lowest p-10 rounded-3xl shadow-sm hover:shadow-md transition-shadow group">
          <div class="w-16 h-16 bg-tertiary-container/10 rounded-2xl flex items-center justify-center mb-6 text-tertiary group-hover:bg-tertiary-container group-hover:text-white transition-all">
            <span class="material-symbols-outlined text-4xl" data-icon="verified">verified</span>
          </div>
          <h3 class="text-2xl font-bold text-primary mb-4">منهج جزائري معتمد</h3>
          <p class="text-on-surface-variant leading-relaxed">كل محتوياتنا مصممة وفقاً للمنهاج الرسمي لوزارة التربية الوطنية الجزائرية، بالتعاون مع نخبة من الأساتذة.</p>
        </div>
      </div>
    </div>
  </section>
</template>
