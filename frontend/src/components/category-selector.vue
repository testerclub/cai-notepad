<template>
  <div class="category">
    <button
      class="btn btn-secondary dropdown-toggle btn-raised"
      type="button"
      @click="dropdown()"
    >
      <i class="fa fa-folder"></i> <span class="category-name">{{selected ? selected.name : "Unassigned"}}</span>
    </button>
    <nav
      v-if="showCategorySelector"
      class="selector"
    >
      <ul
        class="selector-group"
        @blur="close()"
      >
        <li
          class="selector-item zebra"
          :class="{selected: selected === null}"
        >
          <span @click="itemSelected(null)">Unassigned</span>
        </li>
        <category-item
          v-for="(item, index) in categories"
          :key="index"
          v-on:itemSelected="itemSelected"
          :model="item"
          :selected="selected"
        />
      </ul>
    </nav>
  </div>
</template>

<script>
import zebrafy from '@/utils/zebrafy';
import { mapState, mapActions, mapMutations, mapGetters } from 'vuex';
import CategoryItem from './category-item.vue';

export default {
  name: 'CategorySelector',

  props: {
    selected: { type: Object, default: null }
  },

  components: {
    CategoryItem
  },

  created () {
    this.$store.dispatch('Categories/fetchAll');
  },

  data () {
    return {
      showCategorySelector: false
    };
  },

  computed: {
    ...mapState('Categories', { categories: 'itemTree' })
  },

  methods: {
    dropdown () {
      this.showCategorySelector = !this.showCategorySelector;
    },

    close () {
      this.showCategorySelector = false;
    },
    itemSelected (category) {
      this.$emit('selected', category);
      this.showCategorySelector = false;
    }
  },

  updated () {
    zebrafy(this.$el);
  }
};
</script>

<style lang="scss" scoped>
@import "@/scss/_mixins.scss";
@import "@/scss/__category_selector.scss";
.category {
  .category-name {
    display: none;
    @include respond-to(lg) {
      display: inline;
    }
  }
}
</style>
