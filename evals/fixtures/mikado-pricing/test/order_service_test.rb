# frozen_string_literal: true

require "minitest/autorun"
require_relative "../lib/order"
require_relative "../lib/order_service"

class OrderServiceTest < Minitest::Test
  def test_checkout_prices_the_order_with_tax
    order = Order.new(id: 7, lines: [Line.new(sku: "pen", unit_pence: 150, quantity: 2)])

    assert_equal({ order_id: 7, total_pence: 360 }, OrderService.new.checkout(order))
  end
end
