# frozen_string_literal: true

require "minitest/autorun"
require_relative "../lib/order"
require_relative "../lib/pricing_engine"

class PricingEngineTest < Minitest::Test
  def test_price_adds_tax_to_the_subtotal
    lines = [Line.new(sku: "pen", unit_pence: 150, quantity: 2)]

    assert_equal 360, PricingEngine.new(tax_percent: 20).price(lines)
  end
end
