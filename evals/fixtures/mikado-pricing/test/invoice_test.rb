# frozen_string_literal: true

require "minitest/autorun"
require_relative "../lib/order"
require_relative "../lib/invoice"

class InvoiceTest < Minitest::Test
  def setup
    @order = Order.new(
      id: 9,
      lines: [
        Line.new(sku: "ink", unit_pence: 500, quantity: 1),
        Line.new(sku: "pad", unit_pence: 250, quantity: 2)
      ]
    )
  end

  def test_total_includes_tax
    assert_equal 1200, Invoice.new(@order).total_pence
  end

  def test_summary_shows_the_total
    assert_equal "Order 9: 2 lines, 1200p", Invoice.new(@order).summary
  end
end
